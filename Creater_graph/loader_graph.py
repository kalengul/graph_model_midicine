import json

import networkx as nx

# Загрузка графа из json файла
def load_graph_from_json(filename, direction = "Graph"):
    
    # Выбор ориентации
    if direction =="DiGraph":
        G = nx.DiGraph()
    else:
        G = nx.Graph()

    # Загрузка файла
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Добавление узлов в граф
    for node in data['nodes']:
        node_id = node.pop('id')
        G.add_node(node_id, **node)
    
    # Добавление рёбер в граф
    for edge in data['links']:
        source = edge.pop('source')
        target = edge.pop('target')
        G.add_edge(source, target, **edge)
    
    return G