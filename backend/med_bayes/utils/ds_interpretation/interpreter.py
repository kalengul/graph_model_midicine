from typing import Any

import networkx as nx

from med_bayes.utils.ds_interpretation.masses import make_mass, Mass
from med_bayes.utils.ds_interpretation.conf import k_by_length



def _nx_graph(data: dict) -> nx.DiGraph:
    g = nx.DiGraph()

    for n in data["nodes"]:
        g.add_node(n["id"], **n)

    if data.get("links"):
        for link in data["links"]:
            g.add_edge(link["source"], link["target"])
        return g

    for n in data["nodes"]:
        for p in n.get("parents", []):
            g.add_edge(p, n["id"])

    return g


def _side_effects(data: dict) -> dict[str, str]:
    """id → name только для side-effect-узлов."""
    return {
        n["id"]: n["name"]
        for n in data["nodes"]
        if n.get("label") in {"side_e", "side_effect", "effect"}
    }


def _paths(g: nx.DiGraph, src: str, dst: str, cut: int = 8):
    if src in g and dst in g and nx.has_path(g, src, dst):
        yield from nx.all_simple_paths(g, src, dst, cutoff=cut)


def tdsh_interpret(
    *,
    graph_data: dict,
    final_probs: dict[str, float],
    selected_prepare_ids: set[str],
) -> dict[str, dict[str, Any]]:
    """
    Возвращает словарь  se_name → {...}
    (без каких-либо вербальных меток, только цифры и пути)
    """
    g = _nx_graph(graph_data)
    nodes = {n["id"]: n["name"] for n in graph_data["nodes"]}
    se_id2name = _side_effects(graph_data)

    out: dict[str, dict[str, Any]] = {}

    for se_id, se_name in se_id2name.items():
        p = float(final_probs.get(se_id, 0.0))
        combined: Mass | None = None
        paths_out: list[dict] = []
        path_count = 0

        for drug_id in selected_prepare_ids:
            for path in _paths(g, drug_id, se_id):
                k = k_by_length(len(path) - 1)
                m = make_mass(p, k)
                combined = m if combined is None else combined.combine(m)
                path_count += 1

                if len(paths_out) < 3:
                    paths_out.append({
                        "drug": nodes[drug_id],
                        "length": len(path) - 1,
                        "k": round(k, 4),
                        "chain": " → ".join(nodes[n] for n in path)
                    })

        if combined is None:
            continue

        out[se_name] = {
            "belief": round(combined.belief, 6),
            "plausibility": round(combined.plausibility, 6),
            "uncertainty": round(combined.plausibility - combined.belief, 6),
            "path_count": path_count,
            "paths": paths_out
        }

    return out
