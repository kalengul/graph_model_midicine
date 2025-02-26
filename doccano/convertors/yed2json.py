import json
import networkx as nx
import re

filename = 'data\\graph_data_yEd_edit\\drug_amlodipin_perindopril_kaptopril_karvedilol.graphml'
graph = nx.read_graphml(filename)

filename_save = 'data\\graph_data_polina\\drug_amlodipin_perindopril_kaptopril_karvedilol.json'

graph_out = nx.DiGraph()

# Получение списка вершин с атрибутами
nodes = list(graph.nodes(data=True))
print("Список вершин:")
if not nodes:
    print("Нет вершин в графе.")
else:
    for node, attrs in nodes:
        text = attrs.get('label', '')  # Используем get, чтобы избежать ошибки, если 'label' нет
        pattern = r"^(.*?)\(([^)]+)\)\s*$"  # Исправленный паттерн
        matches = re.findall(pattern, text)
        for word, extra in matches:
            graph_out.add_node(word, label=extra if extra else '', weight=5)

# Получение списка рёбер с атрибутами
edges = list(graph.edges(data=True))
print("\nСписок рёбер:")
if not edges:
    print("Нет рёбер в графе.")
else:
    for source, target, attrs in edges:
        label_s = graph.nodes[source].get('label', 'Unknown')  # Получаем узел по id
        label_t = graph.nodes[target].get('label', 'Unknown')

        # # text = attrs.get('label', '')  # Используем get, чтобы избежать ошибки, если 'label' нет
        # # text = attrs.get('label', '')  # Используем get, чтобы избежать ошибки, если 'label' нет


        

        print(source)
        print(target)
        # id_s = source.get('id', '')
        # id_t = target.get('id', '')
        label_s = graph.nodes[source].get('label', 'Unknown')  # Получаем узел по id
        label_t = graph.nodes[target].get('label', 'Unknown')

        pattern = r"^(.*?)\(([^)]+)\)\s*$"  # Исправленный паттерн
        matches_s = re.findall(pattern, label_s)
        matches_t = re.findall(pattern, label_t)

        word

        for word, extra in matches_s:
            word_s = word
            # graph_out.add_node(word, label=extra if extra else '', weight=5)

        for word, extra in matches_t:
            word_t = word
            # graph_out.add_node(word, label=extra if extra else '', weight=5)


        # label_s = node_s.get('label', 'Unknown')  # Получаем label узла
        # label_t = node_t.get('label', 'Unknown')
        # print(id_s)
        # if source in graph_out and target in graph_out:  # Проверяем существование вершин
        graph_out.add_edge(word_s, word_t)  # Добавляем атрибуты рёбер

# Преобразуем исправленный граф в формат JSON
data = nx.node_link_data(graph_out)
with open(filename_save, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Граф сохранён в {filename_save}")
