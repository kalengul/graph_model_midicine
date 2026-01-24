"""Модуль удаления не родственных вершин."""

from abc import ABC, abstractmethod
import json

import networkx as nx


ID_KEY = 'id'
ROOTS_KEY = 'roots'


class NonRelativeNodesDeleter(ABC):
    """Класс удаления не родственных вершин."""

    @abstractmethod
    def delete_nodes(self, graph, most_relative_nodes, roots):
        """Удаление не родственных вершин."""


class SimpleNonRelativeNodesDeleter(NonRelativeNodesDeleter):
    """
    Класс удаления не родственных вершин.

    Класс реализует простой способ удаления
    не родственных вершин.
    Удаляются вершины не имеющние среди предков вершины
    из списка roots.
    """

    def delete_nodes(self, graph, most_relative_nodes, roots):
        """Удаление не родственных вершин."""
        root_set = set(roots)
        for node in most_relative_nodes:
            if not (set(node[ROOTS_KEY]) & root_set):
                graph.remove_node(node[ID_KEY])
        return graph


class SmartNonRelativeNodesDeleter(NonRelativeNodesDeleter):
    """Класс умного удаления не родственных вершин.

    Класс реализует "умный" способ удаления
    не родственных вершин.
    Удаляются вершины не имеющние среди предков вершины
    из списка roots и я вляющиеся наиблизжайшими предками
    для вершин, которое имею предков среди roots.
    """

    def _exist_common_descendant(self, node, graph, most_relative_nodes,
                                 roots):
        """
        Проверка ближайших потомком.

        Проверяет ли вершина node потомка,
        у которого есть предки среди roots.
        """
        for n in graph.neighbors(node):
            for mrn in most_relative_nodes:
                if mrn[ID_KEY] == n and set(mrn[ROOTS_KEY]) & roots:
                    return True
        return False

    def delete_nodes(self, graph, most_relative_nodes, roots):
        """Удаление не родственных вершин."""
        roots_set = set(roots)
        for node in most_relative_nodes:
            if (set(node[ROOTS_KEY]) & roots_set):
                continue
            elif self._exist_common_descendant(node[ID_KEY], graph,
                                               most_relative_nodes, roots_set):
                continue
            else:
                graph.remove_node(node[ID_KEY])
        return graph


def main():
    """Точка входа в программу."""
    roots = ['bafa3390-eb65-46ce-918f-c0790fbc30c3',
             'd35a187a-342e-4ab9-9e2e-9ad33101dda9']
    with open('node_with_roots.json', 'r', encoding='utf-8') as f:
        most_relative_nodes = json.load(f)

    json_graph_path = (
        'C:\\for the job\\graph_model_midicine\\backend'
        '\\data/graphs_for_bayes\\graphs_10_3_optimized_weights.json')

    with open(json_graph_path, 'r', encoding='utf-8') as f:
        graph = nx.node_link_graph(json.load(f), edges='links')
        graph2 = graph.copy()

    processed_graph = SimpleNonRelativeNodesDeleter().delete_nodes(
        graph,
        most_relative_nodes,
        roots)

    with open('simple_processed_graph.json', 'w', encoding='utf-8') as f:
        json.dump(nx.node_link_data(processed_graph, edges='links'), f,
                  ensure_ascii=False, indent=4)

    processed_graph = SmartNonRelativeNodesDeleter().delete_nodes(
        graph2,
        most_relative_nodes,
        roots)

    with open('smart_processed_graph.json', 'w', encoding='utf-8') as f:
        json.dump(nx.node_link_data(processed_graph, edges='links'), f,
                  ensure_ascii=False, indent=4)

    print('Из графа удалены не родственные вершины.')


if __name__ == '__main__':
    main()
