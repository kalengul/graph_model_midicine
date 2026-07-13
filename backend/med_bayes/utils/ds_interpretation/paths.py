"""
Структурный слой ТДШ: построение графа, поиск путей drug → side_effect
и их кластеризация по общему узлу-механизму.

Всё в этом модуле зависит только от графа и набора выбранных
препаратов — не от байесовских вероятностей. Это осознанное
разделение: структурная часть (эта) не меняется, пока не меняется
граф или набор выбранных препаратов, и в отличие от расчёта масс
(interpreter.py) её можно кэшировать между запросами с одной и той
же комбинацией препаратов.
"""

from dataclasses import dataclass

import networkx as nx

from med_bayes.utils.ds_interpretation.conf import (
    MAX_PATH_LENGTH,
    MECHANISM_LABEL,
    k_by_length,
)

SIDE_EFFECT_LABELS = ("side_e", "side_effect", "effect")


def build_nx_graph(graph_data: dict) -> nx.DiGraph:
    """Преобразование JSON-графа в nx.DiGraph."""

    graph = nx.DiGraph()

    for node in graph_data.get("nodes", []):
        graph.add_node(node["id"], **node)

    if graph_data.get("links"):
        for link in graph_data["links"]:
            graph.add_edge(link["source"], link["target"])
        return graph

    for node in graph_data.get("nodes", []):
        target_id = node["id"]
        for parent_id in node.get("parents", []):
            graph.add_edge(parent_id, target_id)

    return graph


def get_side_effect_ids(graph_data: dict) -> list[str]:
    """Получение id узлов побочных эффектов."""

    return [
        node["id"]
        for node in graph_data.get("nodes", [])
        if node.get("label") in SIDE_EFFECT_LABELS
    ]


def iter_drug_to_effect_paths(graph: nx.DiGraph, drug_id: str, effect_id: str):
    """Поиск всех простых путей от препарата до побочного эффекта."""

    if drug_id not in graph or effect_id not in graph:
        return

    # all_simple_paths сам по себе корректно отдаёт пустой генератор
    # для недостижимых пар узлов, отдельная проверка has_path() не нужна
    # и только удваивает обход графа.
    yield from nx.all_simple_paths(
        graph,
        source=drug_id,
        target=effect_id,
        cutoff=MAX_PATH_LENGTH,
    )


@dataclass(frozen=True)
class DrugEffectPath:
    """Один найденный путь drug → side_effect с уже посчитанным k и кластером."""

    drug_id: str
    node_ids: tuple[str, ...]
    length: int
    k: float
    cluster_key: str


def _cluster_key(drug_id: str, node_ids: tuple[str, ...], graph: nx.DiGraph) -> str:
    """
    Ключ кластеризации по общему узлу-механизму.

    Пути, расходящиеся только после общего mechanism-узла, — это одно
    и то же свидетельство, пересказанное несколько раз (разной длины),
    а не независимые источники. Интерпретатор комбинирует такие пути
    не через Демпстера, а берёт одного представителя на кластер.

    Путь без mechanism-узла среди промежуточных ни с чем не группируется
    и остаётся собственным кластером — у нас нет принципиального
    основания считать его зависимым с другими путями этого препарата.
    """

    intermediate = node_ids[1:-1]

    for node_id in intermediate:
        if graph.nodes[node_id].get("label") == MECHANISM_LABEL:
            return f"mech:{node_id}"

    if not intermediate:
        return f"direct:{drug_id}:{node_ids[-1]}"

    return f"path:{'-'.join(node_ids)}"


def find_clustered_paths(
    graph: nx.DiGraph,
    drug_ids: set[str],
    effect_id: str,
) -> dict[str, list[DrugEffectPath]]:
    """
    Находит все пути от каждого из drug_ids до effect_id и размечает
    их cluster_key. Финальную дедупликацию (выбор представителя на
    кластер) делает интерпретатор — здесь только структура.

    Возвращает {drug_id: [DrugEffectPath, ...]}; препараты, для
    которых пути не найдены, в словарь не попадают.
    """

    result: dict[str, list[DrugEffectPath]] = {}

    for drug_id in drug_ids:
        found: list[DrugEffectPath] = []

        for path in iter_drug_to_effect_paths(graph, drug_id, effect_id):
            node_ids = tuple(path)
            length = len(node_ids) - 1
            found.append(
                DrugEffectPath(
                    drug_id=drug_id,
                    node_ids=node_ids,
                    length=length,
                    k=k_by_length(length),
                    cluster_key=_cluster_key(drug_id, node_ids, graph),
                )
            )

        if found:
            result[drug_id] = found

    return result
