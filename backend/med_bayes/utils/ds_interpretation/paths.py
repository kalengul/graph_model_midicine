import networkx as nx

from med_bayes.utils.ds_interpretation.conf import (
    DEFAULT_K,
    K_BY_LENGTH,
    MAX_PATH_LENGTH,
)


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
        if node.get("label") in ("side_e", "side_effect", "effect")
    ]


def length_to_confidence(length: int) -> float:
    """Преобразование длины пути в коэффициент уверенности."""

    return K_BY_LENGTH.get(length, DEFAULT_K)


def iter_drug_to_effect_paths(
    graph: nx.DiGraph,
    drug_id: str,
    effect_id: str,
):
    """Поиск всех простых путей от препарата до побочного эффекта."""

    if drug_id not in graph or effect_id not in graph:
        return

    if not nx.has_path(graph, drug_id, effect_id):
        return

    yield from nx.all_simple_paths(
        graph,
        source=drug_id,
        target=effect_id,
        cutoff=MAX_PATH_LENGTH,
    )
