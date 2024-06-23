import os
import json

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

# Путь к папке с JSON файлами
folder_path = 'json_drug_without_chapter'

# Собираем все тексты из JSON файлов
all_texts = []
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            texts = extract_text(data)
            all_texts.extend(texts)

# Запись всех текстов в один файл для обучения FastText
with open('corpus.txt', 'w', encoding='utf-8') as f:
    for text in all_texts:
        f.write(text + '\n')
