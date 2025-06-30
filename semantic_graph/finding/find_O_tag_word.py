import json
import pymorphy3
import re

morph = pymorphy3.MorphAnalyzer()

# Загрузка данных из JSON-файла
with open('train_model\\mark_sent_1.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

unique_words = set()

# Обработка каждого элемента в JSON
for item in data:
    tokens = item['tokens']
    tags = item['tags']
    
    # Извлечение токенов с меткой "O" и их лемматизация
    for token, tag in zip(tokens, tags):
        if tag == 'O' and re.search(r'[\\/-–]', token):
            unique_words.add(morph.parse(token)[0].normal_form)


# Загрузка данных из JSON-файла
with open('train_model\\words_O_tag.txt', 'w', encoding='utf-8') as file:
    for word in sorted(unique_words):
        file.write(word+'\n')