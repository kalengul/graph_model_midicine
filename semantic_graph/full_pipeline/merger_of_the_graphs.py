import json

import networkx as nx
import matplotlib.pyplot as plt

from create_graph import creat_praph
from loader_graph import load_graph_from_json
from show_graph import plot_graph

def merge_graphs(graphs):
    """
    Объединяет несколько графов, сохраняя и объединяя мета-данные узлов.
    
    Args:
        graphs (list): Список графов для объединения.
    
    Returns:
        networkx.Graph: Новый граф с объединенными узлами, ребрами и мета-данными.
    """
    merged_graph = nx.Graph()

    for graph in graphs:
        for node, data in graph.nodes(data=True):
            if node in merged_graph:
                pass
                # Объединяем мета-данные узлов
                # merged_graph.nodes[node]['positions'] += data['positions']
            else:
                merged_graph.add_node(node, **data)
        
        # Объединение рёбер и их мета-данных
        for u, v, edge_data in graph.edges(data=True):
            if merged_graph.has_edge(u, v):
                # Объединяем мета-данные рёбер, если ребро уже существует
                for key, value in edge_data.items():
                    if key in merged_graph[u][v]:
                        merged_graph[u][v][key] += value
                    else:
                        merged_graph[u][v][key] = value
            else:
                merged_graph.add_edge(u, v, **edge_data)

    return merged_graph

graphs = list()
# COUNT = 2

# GRAPH_DIR = 'I:\datasets\For the job\json_drug_without_chapter'
# GRAPH_DIR = 'json_drug_without_chapter'
GRAPH_DIR = 'full_pipeline'
# GRAPH_DIR = ''

file_names = [
                f'{GRAPH_DIR}\\amiodaron.json',
                f'{GRAPH_DIR}\\metronidazol.json',
            ]

# file_names = [
#                 f'amiodaron.json',
#                 # f'metronidazol.json',
#             ]

for file_name in file_names:
    graph = creat_praph(file_name)
    # plot_graph(graph)
    graphs.append(graph)

output_file = 'full_pipeline\\merge_graphs.json'
merged_graph = merge_graphs(graphs)

# Отрисовка графа
plot_graph(merged_graph, edge_label= True)

with open(output_file, 'w', encoding='utf-8') as file:
    data = nx.node_link_data(merged_graph)
    json.dump(data, file, ensure_ascii=False, indent=4)
print('Слияние графов успешно выполнено!')