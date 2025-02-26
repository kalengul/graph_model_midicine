import sys
import json
import os
import pandas as pd
import networkx as nx
sys.path.append("")
import re

from convertors.BIO2umf import BIO2umf_tt
from convertors.graph2yEd import graph2yEd
from convertors.normalize_text import normalize_text
# from convertors.graph2yEd import graph2yEd_1

# import pymorphy3
from CustomPymorphy.CustomPymorphy import EnhancedMorphAnalyzer
morph = EnhancedMorphAnalyzer()

from convertors.jsonl2BIO import prepare_file

# Директории
dir_drug_data = "data\\drug_data"
dir_drug_links = "data\\drug_links"
dir_drug_yEd_graphs = "data\\graph_data_yEd"
dir_drug_gexf_graphs = "data\\graph_data_gexf"
dir_drug_graphs = "data\\graph_data_polina"

# Функция для лемматизации текста
def lemmatize_text(text):
    if pd.isna(text):  # Обработка пропущенных значений
        return ''
    # words = text.split()
    words = re.findall(r'\w+|[^\w\s]', text)
    lemmatized = [morph.parse(word)[0].normal_form for word in words]

    connected_words = ' '.join(lemmatized)
    rezult_text = normalize_text(connected_words)

    # print("text:", text, "words:", words, "rezult_text:", rezult_text)

    return rezult_text

def csv2graph(G, filename):

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

    # Чтение данных из CSV
    df = pd.read_csv(filename, sep='$', engine='python')  # Разделитель '||'

    # Создание NetworkX графа
    # G = nx.DiGraph()

    # Добавление узлов и ребер с лемматизированными данными
    for _, row in df.iterrows():
        edge_name = row['type']

        # Пропускаем связи с типом "Not_link"
        if (edge_name == "Not_link"):
            continue

        from_node = lemmatize_text(row['from'])
        to_node = lemmatize_text(row['to'])

        # from_label = row['label_from']
        # to_label = row['label_to']

        # Добавляем узлы и ребра
        # add_link(G, from_node, to_node, from_label, to_label, edge_name)
        # G.add_node(from_node, label=from_label, weight=5)
        # G.add_node(to_node, label=to_label, weight=5)
        G.add_edge(from_node, to_node)

    return G

def add_nodes(G, entities):
    for ent in entities:
        token, tag = ent[0], ent[1]

        # Пропускать эти теги
        if tag in ("precsribtion", "condition", "illness", "recomendation", "distribution"):
            continue

        if tag is not None:
            token_lemma = lemmatize_text(token)
            
            if not G.has_node(token_lemma):
                G.add_node(token_lemma, label=tag, weight=5)
            
                # # Проверка текущего узла
                # current_label = G.nodes[token_lemma].get("label", "No label")

                # if current_label == 'No label':
                #     print(current_label, tag)
    return G

def add_edges(G, from_node, to_node):
    def normalize_node(node):
        return lemmatize_text(node).strip().lower()

    # Нормализуем узлы
    from_node_lemm = normalize_node(from_node)
    to_node_lemm = normalize_node(to_node)

    # Проверяем существование узлов
    if not G.has_node(from_node_lemm):
        # print(f"Ошибка: узел {from_node_lemm} отсутствует в графе.")
        return G

    if not G.has_node(to_node_lemm):
        # print(f"Ошибка: узел {to_node_lemm} отсутствует в графе.")
        return G

    # Добавляем ребро
    G.add_edge(from_node_lemm, to_node_lemm)
    # print(f"Успешно добавлено ребро: {from_node_lemm} -> {to_node_lemm}")
    return G


def read_graphml(filename):
    import networkx as nx

    # Чтение графа из файла graphml
    graph = nx.read_graphml(filename)

    # Получение списка вершин с атрибутами
    nodes = list(graph.nodes(data=True))
    print("Список вершин:")
    if not nodes:
        print("Нет вершин в графе.")
    else:
        for node, attrs in nodes:
            print(f"Вершина: {node}, Атрибуты: {attrs}")

    # Получение списка рёбер с атрибутами
    edges = list(graph.edges(data=True))
    print("\nСписок рёбер:")
    if not edges:
        print("Нет рёбер в графе.")
    else:
        for source, target, attrs in edges:
            print(f"Ребро: {source} -> {target}, Атрибуты: {attrs}")

    return

# Проходим по всем файлам в директории
for i, filename in enumerate(os.listdir(dir_drug_data)):
    if filename.endswith('.jsonl'):  # Только файлы с расширением .jsonl

        # Обработка 
        result = prepare_file(f"{dir_drug_data}\\{filename}")

        filename_link = f"{dir_drug_links}\\drug_{i}.csv"
        filename_graph = f"{dir_drug_graphs}\\drug_{i}.json"
        file_name_yEd_graph = f"{dir_drug_yEd_graphs}\\drug_{i}.graphml"
        filename_gexf_graph = f"{dir_drug_gexf_graphs}\\drug_{i}.gexf"

        G = nx.DiGraph()
    
        # Запись связей
        with open(filename_link, 'w', encoding='utf-8') as file_rel:
            file_rel.write("from$label_from$sent_from$type$to$label_to$sent_to\n")
            for sent_list in result:
                for item in sent_list:

                    # Использовать BIO сущности
                    # entites = BIO2umf_tt(item["token_tag_dict"]["tokens"], item["token_tag_dict"]["tags"])
                    entites = item["entities"]
                    G = add_nodes(G, entites)

                    for relation in (item["relations"]+item["missing_relations"]):
                        entity_from, label_from, text_from, relation_type, entity_to, label_to, text_to = relation
                        write_line = f"{entity_from}${label_from}${text_from}${relation_type}${entity_to}${label_to}${text_to}\n"
                       
                        write_line = write_line.replace("( ", "(")
                        # write_line = write_line.replace("||", "$")
                        # write_line = write_line.replace("•", "*")
                        file_rel.write(write_line)

                        if relation_type != "Not_link":
                            G = add_edges(G, entity_from, entity_to)

        # G = csv2graph(G, filename_link)

        # data = nx.node_link_data(G, edges="links")  # Преобразуем граф в формат, совместимый с JSON
        # with open(filename_graph, 'w', encoding='utf-8') as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)

        # Экспортируем граф в формат GEXF
        nx.write_gexf(G, filename_gexf_graph)

        yEd_graph = graph2yEd(G)
        with open(file_name_yEd_graph, "w", encoding="utf-8") as f:
            f.write(yEd_graph)

        # graph_load = read_graphml(file_name_yEd_graph)
