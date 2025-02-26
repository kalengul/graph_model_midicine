
import pandas as pd
import networkx as nx

import pymorphy3
morph = pymorphy3.MorphAnalyzer()


def csv2graph(filename):

    # Функция для лемматизации текста
    def lemmatize_text(text):
        if pd.isna(text):  # Обработка пропущенных значений
            return ''
        words = text.split()
        lemmatized = [morph.parse(word)[0].normal_form for word in words]
        return ' '.join(lemmatized)
    
    # Чтение данных из CSV
    df = pd.read_csv(filename, sep='$', engine='python')  # Разделитель '||'

    # Создание NetworkX графа
    G = nx.DiGraph()

    # Добавление узлов и ребер с лемматизированными данными
    for _, row in df.iterrows():
        edge_name = row['type']

        # Пропускаем связи с типом "Not_link"
        if (edge_name == "Not_link"):
            continue

        from_node = lemmatize_text(row['from'])
        to_node = lemmatize_text(row['to'])

        from_label = row['label_from']
        to_label = row['label_to']

        # Добавляем узлы и ребра
        # add_link(G, from_node, to_node, from_label, to_label, edge_name)
        G.add_node(from_node, name=from_node, label=from_label, weight=5)
        G.add_node(to_node, name=to_node, label=to_label, weight=5)
        G.add_edge(from_node, to_node)

    return G


    # def add_link(G, from_node, to_node, from_label, to_label, edge_name):
    #     # Добавляем узлы и ребра
    #     G.add_node(from_node,
    #                label=f"{from_node}({from_label})",
    #                viz={'font': {'family': 'Arial', 'size': 7, 'style': 'bold'},
    #                     'size':3,
    #                     })
    #     G.add_node(to_node,
    #                label=f"{to_node}({to_label})",
    #                viz={'font': {'family': 'Arial', 'size': 7, 'style': 'bold'},
    #                     'size':3,
    #                     })
    #     G.add_edge(from_node,
    #                to_node,
    #                label=edge_name,
    #                viz={'color':{'r': 255, 'g': 0, 'b': 0, 'a': 1.0},
    #                     'font': {'family': 'Arial', 'size': 10, 'style': 'bold'}
    #                 })

    # def custom_add_node(G, name, label):
    # G.add_node(name, label=f"{name}({label})", viz={'font-family': 'Arial', 'font-size': 10})

    # def custom_add_edge(G, name, label):
    #     G.add_edge(from_node, to_node, title=edge_name)
