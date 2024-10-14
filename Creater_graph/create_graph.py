from split_sent_razdel import split_format_text         # Форматирование и разделение на предложения
from mark_sent_1 import mark_lines                      # Маркировка текста BIO
from highlight_words import find_connections            # Определение связей

import json
import os

import uuid

# Печать списков в столбец
def print_list(list, label = None):
    if label:
        print(f'{label}:')

    # Если список пуст
    if not list or list == []:
        print('\tСписок пуст\n')
        return
    else:
        for item in list:
            print(f'\t{item}')
    print()

# drug_name = "Амиадарон"
# text_list =[
# "Связываясь с бензодиазепиновыми и ГАМКергическими рецепторами, вызывает торможение лимбической системы, таламуса, гипоталамуса, полисинаптических спинальных рефлексов.",
# "После приема внутрь быстро абсорбируется из ЖКТ . Cmax достигается через 1–2 ч. Связывание с белками плазмы составляет 80%. Проходит через ГЭБ и плацентарный барьер, проникает в грудное молоко. Метаболизируется в печени. T1/2 — 16 ч. Выводится преимущественно почками. Повторное назначение с интервалом менее 8–12 ч может приводить к кумуляции.",
# "Гиперчувствительность, выраженная дыхательная недостаточность, глаукома (острый приступ), острые заболевания печени и почек, миастения, беременность (особенно I триместр), кормление рудью, возраст до 18 лет.",
# "Открытоугольная глаукома, апноэ во время сна, хроническая почечная и/или печеночная недостаточность, алкогольное поражение печени.",
# "Категория действия на плод по FDA — D.",
# "Сонливость, усталость, головокружение, шаткость походки, замедление психических и двигательных реакций, снижение концентрации внимания, тошнота, запор, дисменорея, снижение либидо, кожный зуд, парадоксальные реакции (агрессивность, возбуждение, раздражительность, тревожность, галлюцинации), привыкание, лекарственная зависимость, синдром отмены.",
# "Усиливает действие алкоголя, нейролептиков и снотворных средств, наркотических анальгетиков, центральных миорелаксантов. Увеличивает концентрацию имипрамина в сыворотке.",
# "Симптомы: угнетение ЦНС различной степени выраженности (от сонливости до комы) — сонливость, спутанность сознания; в более тяжелых случаях (особенно на фоне приема других ЛС, угнетающих ЦНС , или алкоголя) — атаксия, снижение рефлексов, гипотензия, кома.",
# "Лечение: индукция рвоты, промывание желудка, симптоматическая терапия, мониторинг жизненно важных функций. При выраженной гипотензии — введение норэпинефрина. Специфический антидот — антагонист бензодиазепиновых рецепторов флумазенил (введение только в условиях стационара)."
# ]


# На вход подаётся список предложений из json файла инструкции
def create_gragh_json(drug_name, text_list):

    # Блок Форматирования и разделения на предложения
    text = '\n'.join(text_list)
    sents = split_format_text(text).split('\n')

    # Присваивание меток BIO (можно заменить на нейронку)
    dict_words_tags = mark_lines(sents)

    uuid_drug = str(uuid.uuid4())

    # Словарь
    data_json = {
        "drug_name": drug_name,
        "text_instruction": [item["tokens"] for item in dict_words_tags],
        "nodes": [
                    {
                    "id" : uuid_drug,
                    "line": None,
                    "start": None,
                    "end": None,
                    "name": drug_name,
                    "tag": None,

                    "parent_id": set(),
                    "child_id": set(),

                    "level": 0
                }
        ],
        "links": [],

    }

    # Прохождение по каждому предложению
    for i_line, sent_words_tags in enumerate(dict_words_tags):
        ner_tokens, connections, not_connections = find_connections(sent_words_tags["tokens"], sent_words_tags["tags"])
        
        # Преобразование connections в links
        for item in connections:
            uid_mech = item[0][0]
            uid_word = item[0][0]
            data_json['links'].append({
                    "source_id": uid_mech,
                    "target_id": uid_word,
                })

        # Прикрепление к главной вершине
        for item in not_connections:
            uid = item[0]
            data_json['links'].append({
                    "source_id": uuid_drug,
                    "target_id": uid,
                })

        # Добавление узлов в nodes
        for item in ner_tokens:
            # Определение уровня узла
            level = 1 if item[3] == 'mechanism' else 2

            uid = item[0]

            # Инициализация узла с пустыми множествами для parent_id и child_id
            node = {
                "id": uid,
                "line": i_line,
                "start": item[1],
                "end": item[2],
                "name": ' '.join(item[3]),
                "tag": item[4],
                "parent_id": set(),
                "child_id": set(),
                "level": level
            }

            # Если тег 'mechanism', устанавливаем parent_id как {"0"}
            if item[4] == 'mechanism':
                node["parent_id"].add(uuid_drug)
                
                # Прикрепление механизма к главному узлу
                data_json['links'].append({
                    "source_id": uuid_drug,
                    "target_id": uid,
                })


            data_json['nodes'].append(node)


    # Создание словаря для быстрого доступа к узлам по id
    nodes_dict = {node['id']: node for node in data_json['nodes']}

    # Обновление parent_id и child_id в nodes
    for link in data_json['links']:
        source_id = link['source_id']
        target_id = link['target_id']

        # Обновляем child_id для узла с source_id
        if source_id in nodes_dict:
            nodes_dict[source_id]['child_id'].add(target_id)

        # Обновляем parent_id для узла с target_id
        if target_id in nodes_dict:
            nodes_dict[target_id]['parent_id'].add(source_id)

    # Преобразуем множества в списки для JSON
    for node in data_json['nodes']:
        node['parent_id'] = list(node.get('parent_id', []))
        node['child_id'] = list(node.get('child_id', []))

    return data_json


# Путь к папке
folder_path = 'json_drug_without_chapter'

# Проход по всем файлам в папке
for filename in os.listdir(folder_path):
        
    # Открываем JSON-файл
    with open(f'{folder_path}\\{filename}', 'r', encoding='utf-8') as file:
        data = json.load(file)

    drug_name = data['Название']

    text_list = []
    # Проход по ключам и значениям в JSON
    for key, value in data.items():
        # Проверяем, является ли значение списком строк
        if isinstance(value, list)\
            and all(isinstance(item, str) for item in value)\
            and key != 'Название':
            text_list.extend(value)
        
    data_json = create_gragh_json(drug_name, text_list)

    output_file = f'graph_BIO_folder\\graph_BIO_{drug_name}.json'
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data_json, file, ensure_ascii=False, indent=4)

    print("Граф для", drug_name, "сохранён")


   


