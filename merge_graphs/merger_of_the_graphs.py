from collections import defaultdict
import os
import json
import random


import networkx as nx
import matplotlib.pyplot as plt


from create_graph import creat_praph


def merge_graphs(graphs):
    """
    Объединяет несколько графов, сохраняя и объединяя мета-данные узлов и ребер.
    
    Args:
        graphs (list): Список графов для объединения.
    
    Returns:
        networkx.Graph: Новый граф с объединенными узлами, ребрами и мета-данными.
    """
    merged_graph = nx.Graph()

    for graph in graphs:
        for node, data in graph.nodes(data=True):
            if node in merged_graph:
                # Объединяем мета-данные узлов
                merged_graph.nodes[node]['positions'] += data['positions']
            else:
                merged_graph.add_node(node, **data)
        
        for u, v in graph.edges():
            merged_graph.add_edge(u, v)

    return merged_graph


def load_graph_from_json(filename):
    G = nx.Graph()
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for node in data['nodes']:
        G.add_node(node['id'], **{k: v for k, v in node.items() if k != 'id'})
    for edge in data['links']:
        G.add_edge(edge['source'], edge['target'], **{k: v for k, v in edge.items() if k not in ['source', 'target']})
    return G


graphs = list()
COUNT = 2
GRAPH_DIR = 'I:\datasets\For the job\json_drug_without_chapter'
file_names = [
                f'{GRAPH_DIR}\\amiodaron.json',
                f'{GRAPH_DIR}\\amlodipin.json',
            ]
for file_name in file_names:
    graph = creat_praph(file_name)
    nx.draw(graph, with_labels=True, font_weight='bold')
    plt.show()
    graphs.append(graph)

output_file = 'merge_graphs.json'
merged_graph = merge_graphs(graphs)
nx.draw(merged_graph, with_labels=True, font_weight='bold')
plt.show()
with open(output_file, 'w', encoding='utf-8') as file:
    data = nx.node_link_data(merged_graph)
    json.dump(data, file, ensure_ascii=False, indent=4)
print('Слияние графов успешно выполнено!')