import fasttext

import json
import pymorphy3
import re

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial.distance import cosine

# Загрузка модели
# model = fasttext.load_model('classifier_model.bin')
model = fasttext.load_model('one_corpus\\model_fast_train_dim900_ws15.bin')

# Загрузка ресурсов NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Инициализация морфологического анализатора Pymorphy2
morph = pymorphy3.MorphAnalyzer()

# Русские стоп-слова
stop_words = set(stopwords.words('russian'))


# Функция для предобработки текста
def preprocess_text(text):
    # Токенизация текста на слова
    tokens = word_tokenize(text)

    # Удаление пунктуации и стоп-слов
    tokens = [re.sub(r'\W+', '', token) for token in tokens if re.sub(r'\W+', '', token) and token not in stopwords.words('russian')]

    # Удаление всех чисел
    tokens = [token for token in tokens if not re.fullmatch(r'\d+', token)]

    # Перевод в нижний регистр
    filtered_tokens = [word.lower() for word in tokens]

    # Удаление слов короче 2 букв
    tokens = [token for token in tokens if len(token) >= 2]
    
    # # Удаление стоп-слов и перевод в нижний регистр
    # filtered_tokens = [word.lower() for word in tokens if word.lower() not in stop_words]
    
    # Лемматизация
    lemmatized_tokens = [morph.parse(word)[0].normal_form for word in filtered_tokens]
    
    return lemmatized_tokens

# Функция для создания n-грамм
def create_ngrams(tokens, n):
    return [' '.join(gram) for gram in ngrams(tokens, n)]

# Функция для нахождения косинусного сходства
def cosine_similarity(vec1, vec2):
    return 1 - cosine(vec1, vec2)

# Функция для построения семантического графа
def build_semantic_graph(words, model, name):
    # Создание графа
    G = nx.Graph()

    # Связь между классом и токеном
    thresholds = {  "фармакология": 0.65,
                    "противопоказания": 0.45,
                    "ограничения_к_применению": 0.5,
                    "применение_при_беременности_и_кормлении_грудью": 0.55,
                    "побочные_действия": 0.45,
                    "взаимодействие": 0.55,
                    "передозировка": 0.65,}
    
    # Связь между токенами (нижняя граница)
    thresholds_by_item_down = {  "фармакология": 0.8,
                            "противопоказания": 0.85,
                            "ограничения_к_применению": 0.8,
                            "применение_при_беременности_и_кормлении_грудью": 0.8,
                            "побочные_действия": 0.8,
                            "взаимодействие": 0.83,
                            "передозировка": 0.8,}
    
    # Связь между токенами (верхняя граница)
    thresholds_by_item_up = {  "фармакология": 0.9,
                            "противопоказания": 0.92,
                            "ограничения_к_применению": 0.9,
                            "применение_при_беременности_и_кормлении_грудью": 0.9,
                            "побочные_действия": 0.9,
                            "взаимодействие": 0.9,
                            "передозировка": 0.9,}

    # Добавление вершин для каждого токена
    for key in keys:
        if words[key]:
            for item in words[key]:
                G.add_node(item)

    
    G.add_node(name)
    for key in keys:

        # Добавление узлов -- свойств препарата
        G.add_node(item)
        G.add_edge(name, key)

        # Определение векторов для ключа
        vectors_word_by_key = {item: model.get_word_vector(item) for item in words[key]}
        vectors_key = {item: model.get_word_vector(item) for item in keys}

        # Добавление ребер на основе схожести
        for i, item1 in enumerate(words[key]):
            for j, item2 in enumerate(words[key]):
                if i < j:  # чтобы не дублировать проверки и не сравнивать элемент с самим собой
                    similarity_item1_key = cosine_similarity(vectors_word_by_key[item1], vectors_key[key])
                    similarity_item2_key = cosine_similarity(vectors_word_by_key[item2], vectors_key[key])
                    similarity_item1_item2 = cosine_similarity(vectors_word_by_key[item1], vectors_word_by_key[item2])

                    if similarity_item1_key > thresholds[key] and similarity_item2_key > thresholds[key]:
                        G.add_edge(key, item1)
                        G.add_edge(key, item2)

                        if similarity_item1_item2 > thresholds_by_item_down[key] and similarity_item1_item2 < thresholds_by_item_up[key]:
                            G.add_edge(item1, item2)


    # Удаление изолированных вершин
    isolated_nodes = list(nx.isolates(G))
    G.remove_nodes_from(isolated_nodes)

    # Удаление петель (ребра, которые соединяют вершину саму с собой)
    G.remove_edges_from(nx.selfloop_edges(G))
    
    return G


# Функция для отображения графа с узлами, у которых есть ребра
def plot_graph(G):
    # Визуализация графа
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)  # используется алгоритм размещения узлов
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='skyblue', font_size=8, edge_color='grey')
    plt.show()

# Путь к JSON файлу
json_filepath = 'json_drug_without_chapter\\amiodaron.json'

# Открытие и чтение JSON файла
with open(json_filepath, 'r', encoding='utf-8') as file:
    data = json.load(file)
    name = data['Название']

# Ключевые слова
keys = ["фармакология", "противопоказания", "ограничения_к_применению",
        "применение_при_беременности_и_кормлении_грудью", "побочные_действия",
        "взаимодействие", "передозировка"]

# Словари для хранения обработанных данных
processed_data = {key: [] for key in keys}

# Обработка данных по каждому ключевому слову
for key in keys:
    if data[key]:
        for item in data[key]:

            # Предобработка текста
            lemmatized_tokens = preprocess_text(item)
            
            # Создание биграмм и триграмм
            bigram_tokens = create_ngrams(lemmatized_tokens, 2)
            trigram_tokens = create_ngrams(lemmatized_tokens, 3)

            processed_data[key] += lemmatized_tokens# + bigram_tokens + trigram_tokens
            


# print(processed_data)

# Использования модели для построения графа
G = semantic_graph = build_semantic_graph(processed_data, model, name)

# Отображение графа
plot_graph(semantic_graph)


