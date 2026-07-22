"""
Структурный слой ТДШ: построение графа, поиск путей drug → side_effect
и их кластеризация по пересечению промежуточных узлов.

Всё в этом модуле зависит только от графа и набора выбранных
препаратов — не от байесовских вероятностей. Можно кэшировать между
запросами с одной и той же комбинацией препаратов.

Кластеризация путей внутри препарата намеренно не использует типы
вершин (mechanism/action/...) — это экспертная, не объективная
разметка. Единственный объективный критерий — топология графа: два
пути зависимы, если у них есть общий промежуточный узел (любой, в
т.ч. side_e при связях side_e -> side_e), потому что тогда они
описывают одну и ту же причинно-следственную цепочку, просто разной
длины, а не два независимых источника.
"""

from dataclasses import dataclass

import networkx as nx

from med_bayes.utils.ds_interpretation.conf import MAX_PATH_LENGTH, k_by_length

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

    yield from nx.all_simple_paths(
        graph,
        source=drug_id,
        target=effect_id,
        cutoff=MAX_PATH_LENGTH,
    )


@dataclass(frozen=True)
class DrugEffectPath:
    """Один найденный путь drug → side_effect с уже посчитанным k."""

    drug_id: str
    node_ids: tuple[str, ...]
    length: int
    k: float

    @property
    def intermediate_nodes(self) -> frozenset[str]:
        """Узлы строго между препаратом и эффектом (без концов пути)."""
        return frozenset(self.node_ids[1:-1])


def cluster_paths_by_shared_nodes(
    paths: list[DrugEffectPath],
) -> list[list[DrugEffectPath]]:
    """
    Группирует пути одного препарата по пересечению множества
    промежуточных узлов — union-find по общим узлам.

    Пути без промежуточных узлов (прямая связь prepare -> side_e,
    когда второй слой графа пропущен) ни с чем не пересекаются по
    определению и всегда остаются отдельным кластером из одного пути.

    Связность транзитивна: если путь A пересекается с B, а B — с C
    (по разным узлам), все три — один кластер, даже если A и C общих
    узлов не делят напрямую.
    """

    n = len(paths)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    intermediates = [p.intermediate_nodes for p in paths]

    for i in range(n):
        if not intermediates[i]:
            continue
        for j in range(i + 1, n):
            if intermediates[i] & intermediates[j]:
                union(i, j)

    clusters: dict[int, list[DrugEffectPath]] = {}
    for idx, path in enumerate(paths):
        clusters.setdefault(find(idx), []).append(path)

    return list(clusters.values())


def find_clustered_paths(
    graph: nx.DiGraph,
    drug_ids: set[str],
    effect_id: str,
) -> dict[str, list[list[DrugEffectPath]]]:
    """
    Находит все пути от каждого из drug_ids до effect_id и группирует
    их по пересечению промежуточных узлов.

    Возвращает {drug_id: [[путь, путь, ...], [путь, ...], ...]} —
    список кластеров на препарат; финальный выбор представителя
    внутри кластера и комбинирование между кластерами делает
    интерпретатор. Препараты, для которых пути не найдены, в словарь
    не попадают.
    """

    result: dict[str, list[list[DrugEffectPath]]] = {}

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
                )
            )

        if found:
            result[drug_id] = cluster_paths_by_shared_nodes(found)

    return result
