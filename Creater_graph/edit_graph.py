import uuid
import json

import networkx as nx
from collections import deque

from loader_graph import load_graph_from_json
from show_graph import plot_graph


# Замена id
def id_to_uuid(G):
    # Создание словаря соответствий между старыми id и новыми uuid
    id_to_uuid = {node: str(uuid.uuid4()) for node, data in G.nodes(data=True)}

    # Замена id на uuid в самих объектах
    for node, data in G.nodes(data=True):
        # Заменяем id на новый uuid
        if 'id' in data:  # Проверяем, есть ли поле 'id'
            data['id'] = id_to_uuid[node]
        
        # Замена roots на uuid
        if 'roots' in data and data['roots'] in id_to_uuid:
            data['roots'] = id_to_uuid[data['roots']]
        
        # Обновление позиции, если требуется
        if 'positions' in data:
            for position in data['positions']:
                if position[0] in id_to_uuid:
                    position[0] = id_to_uuid[position[0]]

    # Обновление идентификаторов узлов
    G = nx.relabel_nodes(G, id_to_uuid)

    return G

#  Добавление предков и потомков
def add_child_and_parent(G):

    for node in G.nodes:
        predecessors = list(G.predecessors(node)) if G.is_directed() else []
        successors = list(G.successors(node)) if G.is_directed() else list(G.neighbors(node))
        
        # Обновление узлов с предками и потомками
        G.nodes[node]['parents'] = predecessors
        G.nodes[node]['children'] = successors

    return G


# Добавление уровней
def add_level(G):

    def find_start_node(G):
        # Найти узел с тегом 'drug'
        for node, data in G.nodes(data=True):
            if data.get('tag') == 'drug':
                return node
        return None

    start_node = find_start_node(G)
    if start_node is None:
        raise ValueError("Стартовый узел с тегом 'drug' не найден")

    levels = {node: None for node in G.nodes()}  # Инициализация уровней как None
    levels[start_node] = 0  # Уровень начальной вершины = 0
    queue = deque([start_node])  # Очередь для BFS

    # BFS для определения уровней всех узлов
    while queue:
        current_node = queue.popleft()
        current_level = levels[current_node]

        # Проход по всем соседям текущей вершины
        for neighbor in G.successors(current_node):
            if levels[neighbor] is None:  # Если вершина еще не была посещена
                levels[neighbor] = current_level + 1
                queue.append(neighbor)

    # Обновляем граф, добавляя поле 'level' к каждому узлу
    for node in G.nodes():
        G.nodes[node]['level'] = levels[node]

    return G


# Загрузка графа
G_dir = load_graph_from_json('full_pipeline\\merge_graphs.json',
                             direction="DiGraph")
# Преобразование id
G_dir = id_to_uuid(G_dir)
# Добавление предков и потомков
G_dir = add_child_and_parent(G_dir)
# Добавление уровней
G_dir = add_level(G_dir)

# Сохранение графа
with open('full_pipeline\\edit_graph.json', 'w', encoding='utf-8') as file:
    data = nx.node_link_data(G_dir)

    # Удаление ненужных полей
    data.pop("directed", None)
    data.pop("multigraph", None)
    data.pop("graph", None)

    json.dump(data, file, ensure_ascii=False, indent=4)

# Отображение графа
plot_graph(G_dir)