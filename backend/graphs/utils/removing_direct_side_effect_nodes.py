"""
Модуль для удалиения прямых побочных действий.

Удаляются вершины побочных действий,
которые непосредственно соеденены с вершинами ЛС.
"""

import networkx as nx


PREPARE = 'prepare'
EFFECT = 'side_e'
LABEL = 'label'


def remove_direct_side_effect_nodes(graph):
    """Удаление прямых вершин побочных децствий."""
    to_remove = []
    for u, v in graph.edges():
        label_u = graph.nodes[u].get(LABEL)
        label_v = graph.nodes[v].get(LABEL)

        if ((label_u == PREPARE and label_v == EFFECT)
                or (label_u == PREPARE and label_v == EFFECT)):
            to_remove.append((u, v))

    graph.remove_edges_from(to_remove)
    graph.remove_nodes_from(list(nx.isolates(graph)))
    return graph
