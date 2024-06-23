import networkx as nx
import numpy as np
import fasttext
import json
import pymorphy3

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import re

import matplotlib.pyplot as plt

# Загрузка модели
# model = fasttext.load_model('model_fast_train.bin')
# model = fasttext.load_model('model_fast_train_dim300_ws5.bin')
model = fasttext.load_model('model_fast_train_dim900_ws15.bin')

# Функция для построения семантического графа
def build_semantic_graph(words, model, name):
    G = nx.Graph()
    # for word in words:
    #     if word in model:
    #         G.add_node(word, vector=model[word])

    groups = [
        "фармакология",
        "противопоказания",
        "ограничения_к_применению",
        "применение_при_беременности_и_кормлении_грудью",
        "побочные_действия",
        "взаимодействие",
        "передозировка"
    ]

    G.add_node(name)
    for item in groups:
        G.add_node(item)
        G.add_edge(name, item)

    for i, word1 in enumerate(words):
        for j, group in enumerate(groups):
            if word1 in model and group in model:
                print("Nen")
                similarity = np.dot(model[word1], model[group]) / (np.linalg.norm(model[word1]) * np.linalg.norm(model[group]))
                if similarity > 0.5:  # Пороговое значение для добавления ребра
                    G.add_edge(word1, group, weight=similarity)
                    print(f'{word1} -- {group} similarity: {similarity}')


    # for i, word1 in enumerate(words):
    #     for j, word2 in enumerate(words):
    #         if i < j and word1 in model and word2 in model:
    #             similarity = np.dot(model[word1], model[word2]) / (np.linalg.norm(model[word1]) * np.linalg.norm(model[word2]))
    #             if similarity > 0.82:  # Пороговое значение для добавления ребра
    #                 G.add_edge(word1, word2, weight=similarity)
    #                 print(f'{word1} -- {word2} similarity: {similarity}')
    
    return G

# Функция для отображения графа с узлами, у которых есть ребра
def plot_graph_with_edges(G):
    # Создаем подграф, содержащий только узлы с ребрами
    nodes_with_edges = set()
    for edge in G.edges:
        nodes_with_edges.add(edge[0])
        nodes_with_edges.add(edge[1])
    
    subgraph = G.subgraph(nodes_with_edges)
    
    # Визуализация графа
    pos = nx.spring_layout(subgraph)  # Вычисляем позиции узлов для визуализации
    plt.figure(figsize=(12, 12))
    nx.draw(subgraph, pos, with_labels=True, node_size=500, node_color="skyblue", font_size=10, font_color="black", edge_color="gray")
    plt.show()

# Функция для извлечения текста из JSON файла
def extract_text(json_data):
    texts = []
    for key, value in json_data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for sub_key, sub_value in item.items():
                        texts.append(sub_value)
                else:
                    texts.append(item)
    return texts

drug = 'acetilsalicilovaya_kislota'
drug_text = ''

with open(f'json_drug_without_chapter\\{drug}.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    name = data['Название']
    texts = extract_text(data)
    drug_text = ' '.join(texts)

# Лемматизация текста
morph = pymorphy3.MorphAnalyzer()

def preprocess_text(text):

    # Токенизация и приведение к нижнему регистру
    tokens = word_tokenize(text.lower())

    # Удаление пунктуации и стоп-слов
    tokens = [re.sub(r'\W+', '', token) for token in tokens if re.sub(r'\W+', '', token) and token not in stopwords.words('russian')]

    # Удаление всех чисел
    tokens = [token for token in tokens if not re.fullmatch(r'\d+', token)]
    
    # Удаление римских чисел (например, I, II, III, IV, V, VI, VII, VIII, IX, X и т.д.)
    roman_pattern = re.compile(r'\b(?:X{1,3}(?:IX|IV|V?I{0,3})|IX|IV|V?I{1,3})\b', re.IGNORECASE)
    tokens = [token for token in tokens if not roman_pattern.fullmatch(token)]
    
    # Удаление слов короче 3 букв
    tokens = [token for token in tokens if len(token) >= 3]

    # Лемматизация
    tokens = [morph.parse(token)[0].normal_form for token in tokens]

    return tokens

tokens = preprocess_text(drug_text)
print("Текст нормализирован")
print("tokens:", tokens)

# Удаление повторяющихся элементов
unique_tokens = list(set(tokens))

# Пример использования модели для построения графа
semantic_graph = build_semantic_graph(unique_tokens, model, name)

# Отображение графа
plot_graph_with_edges(semantic_graph)
