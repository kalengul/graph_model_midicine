"""Модуль обходчика."""

import json

import networkx as nx


PATH_JSON_GRAPH = ('C:\\for the job\\graph_model_midicine\\backend'
                   '\\data/graphs_for_bayes\\graphs_10_3_optimized_weights.json')


class Lineman:
    """Обходчик графа."""

    PREPARE_KEY = 'prepare'
    LABEL_KEY = 'label'
    ROOTS_KEY = 'roots'

    def traverse(self, graph):
        """Обход графа."""
        roots = []
        for id, attrs in graph.nodes(data=True):
            if attrs.get(self.LABEL_KEY) == self.PREPARE_KEY:
                roots.append(id)

        other = []
        print('Корни: ', roots)
        for node in graph.nodes():
            node_and_parents = {
                'id': node,
                self.ROOTS_KEY: []
            }
            for root in roots:
                if node in roots:
                    continue
                if nx.has_path(graph, root, node):
                    node_and_parents[self.ROOTS_KEY].append(root)
            if len(node_and_parents[self.ROOTS_KEY]) != 0:
                other.append(node_and_parents)

        return other


def main():
    """Точка входа в программа."""
    with open(PATH_JSON_GRAPH, 'r', encoding='utf-8') as f:
        graph = nx.node_link_graph(json.load(f), edges="links")

    isolated_nodes = list(nx.isolates(graph))
    print("Изолированные вершины:", isolated_nodes)

    result = Lineman().traverse(graph)

    with open('node_with_roots.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print('Обход графа завершился успешно!')


if __name__ == '__main__':
    main()
