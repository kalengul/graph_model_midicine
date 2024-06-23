import os
import json

# Путь к папке с JSON файлами
input_folder = 'json_drug_without_chapter'
output_filepath = 'corpus_keys'

# Названия ключей, по которым будем разбивать данные
keys = [
    "фармакология",
    "противопоказания",
    "ограничения_к_применению",
    "применение_при_беременности_и_кормлении_грудью",
    "побочные_действия",
    "взаимодействие",
    "передозировка"
]

# Инициализация словаря для накопления данных по ключам
collected_data = {key: [] for key in keys}

# Проход по всем файлам в папке
for filename in os.listdir(input_folder):
    if filename.endswith('.json'):
        filepath = os.path.join(input_folder, filename)
        
        # Чтение JSON файла
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Сбор данных по ключам
        for key in keys:
            if key in data:
                collected_data[key].append(data[key])

# Путь для сохранения текстовых файлов
output_folder = 'many_corpus\\corpus_keys'
os.makedirs(output_folder, exist_ok=True)

# Запись собранных данных в отдельные текстовые файлы
for key in keys:
    output_filepath = os.path.join(output_folder, f'{key}.txt')
    with open(output_filepath, 'w', encoding='utf-8') as outfile:
        for item in collected_data[key]:
            if item:
                # Запись каждого элемента списка в отдельную строку
                if isinstance(item, list):  # Если значение в JSON было списком
                    for sub_item in item:
                        outfile.write(f"{sub_item}\n")
                else:  # Если значение было строкой
                    outfile.write(f"{item}\n")