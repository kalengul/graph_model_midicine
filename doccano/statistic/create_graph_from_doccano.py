import pandas as pd
import networkx as nx
from pyvis.network import Network
import pymorphy3

# Инициализация лемматизатора
morph = pymorphy3.MorphAnalyzer()

# Функция для лемматизации текста
def lemmatize_text(text):
    if pd.isna(text):  # Обработка пропущенных значений
        return ''
    words = text.split()
    lemmatized = [morph.parse(word)[0].normal_form for word in words]
    return ' '.join(lemmatized)

# Функция для рекурсивного поиска потомков
def get_descendants(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    descendants = {node}

    # Получаем все дочерние узлы (потомков) с использованием 'successors' для ориентированных графов
    for neighbor in graph.successors(node):
        if neighbor not in visited:
            descendants.update(get_descendants(graph, neighbor, visited))
    
    return descendants

# Чтение данных из CSV
df = pd.read_csv('data\\data_relations_3.csv', sep='$', engine='python')  # Разделитель '||'

# Создание NetworkX графа
G = nx.DiGraph()

# Добавление узлов и ребер с лемматизированными данными
for _, row in df.iterrows():
    from_node = lemmatize_text(row['from'])
    to_node = lemmatize_text(row['to'])

    from_label = row['label_from']
    to_label = row['label_to']

    edge_name = row['type']

    # Пропускаем связи с типом "Not_link" или если метки узлов соответствуют исключениям
    if (edge_name == "Not_link"
        # or from_label in ("condition", "illness", "recommendation", "noun", "banned")
        # or to_label in ("condition", "illness", "recommendation", "noun", "banned")
        ):
        continue

    # Добавляем узлы и ребра
    G.add_node(from_node, label=f"{from_node}({from_label})", weight=5)
    G.add_node(to_node, label=f"{to_node}({to_label})", weight=5)
    G.add_edge(from_node, to_node, title=edge_name)

# Находим узлы без родителей и которые не содержат метки "prepare" или "group"
nodes_without_parents = [
    node for node in G.nodes if G.in_degree(node) == 0
    # and 'prepare' not in G.nodes[node].get('label', '')
    # and 'group' not in G.nodes[node].get('label', '')
    and (
            'action'    in G.nodes[node].get('label', '')
        or 'mechanism' in G.nodes[node].get('label', '')
        or 'side_e' in G.nodes[node].get('label', '')
    )
]

# Шаг 3: Ищем узлы без меток "prepare" или "group"
relevant_nodes = set()
for node in nodes_without_parents:
    print(G.nodes[node].get('label', ''))
    relevant_nodes.update(get_descendants(G, node))

# Шаг 4: Создаем новый граф, содержащий только выбранные узлы и их связи
filtered_graph = G.subgraph(relevant_nodes).copy()

# # Визуализация нового графа с PyVis
# net = Network(notebook=False, directed=True, height='800px', width='100%', bgcolor='#222222', font_color='white')

# # Отключаем физику, чтобы зафиксировать расположение узлов
# options = """
# var options = {
#   "physics": {
#     "enabled": false
#   }
# }
# """
# net.set_options(options)

# # Переносим граф из NetworkX в PyVis
# net.from_nx(filtered_graph)

print("Количество узлов:", filtered_graph.number_of_nodes())
print("Количество ребер:", filtered_graph.number_of_edges())

# # Сохранение графа в HTML-файл
# net.show("data\\graph_visualization.html", notebook=False)
# print("Граф сохранен в файле graph_visualization.html. Откройте его в браузере.")

# Экспортируем граф в формат GEXF
nx.write_gexf(G, "data\\graph_visualization_all.gexf")
