import json
import random
import re

import spacy
from spacy.tokens import DocBin
from spacy.tokenizer import Tokenizer
from spacy.symbols import ORTH

import string

nlp = spacy.load("ru_core_news_lg")  # load other spacy model

# Файлы
# file_1 = "jsons\\data.jsonl"
# file_2 = "jsons\\data_edit.jsonl"
# file_3 = "data_1.jsonl"
file_4 = "data_edit_1.jsonl"

file_log = 'log.txt'  # Имя файла для записи

file_res = 'data_bio.json'  # Имя файла для записи

# Функция для кастомного токенайзера
def custom_tokenizer(nlp):
    # Регулярное выражение, которое разделяет слова, точки и другие знаки отдельно
    infix_re = re.compile(r'''[.\,;\:\!\?\…\-\)\(]''')

    # Создаем токенайзер с кастомными правилами
    return Tokenizer(
        nlp.vocab,
        prefix_search=nlp.tokenizer.prefix_search,
        suffix_search=nlp.tokenizer.suffix_search,
        infix_finditer=infix_re.finditer,  # Используем наше регулярное выражение
        token_match=nlp.tokenizer.token_match,
    )

# Заменяем токенайзер на кастомный
nlp.tokenizer = custom_tokenizer(nlp)

# Очищаем содержимое файла перед записью
with open(file_log, 'w', encoding='utf-8') as file:
    file.write("")

def write_add(file_name, text):
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(text)


# Читаем все данные из файла
with open(file_4, 'r', encoding='utf-8') as file:
    lines = file.readlines()

def convert_data(lines, output_file):
    db = DocBin()  # create a DocBin object
    token_data = []  # List to hold token dictionaries

    result = []

    for line in lines:
        data = json.loads(line)

        # Initialize the dictionary to hold lists of words and tags
        token_data = {
            "words": [],
            "tags": []
        }

        # Текст
        id = data["id"]
        text = data["text"]
        doc = nlp.make_doc(text)

        # Сущности
        entities = data.get("entities", [])
        ents = []

        for item in entities:
            id_w = item["id"]
            start = item["start_offset"]
            end = item["end_offset"]
            label = item["label"]

            # Удаляем пробелы в конце
            while end > start and (text[end-1].isspace() or text[end-1] in (',', '.')):
                end -= 1

            # Удаляем пробелы в начале
            while end > start and (text[start].isspace() or text[start] in (',', '.')):
                start += 1

            span = doc.char_span(start, end, label=label)

            if span:
                ents.append(span)
       
        # Назначаем сущности документу
        doc.ents = ents
        db.add(doc)

        # Извлекаем токены и теги
        for token in doc:
            token_data["words"].append(token.text)
            if token.ent_iob_ != 'O':  # Если токен относится к сущности
                # Проверяем, является ли токен первым в последовательности
                if token.ent_iob_ == 'B':
                    token_data["tags"].append(f'B-{token.ent_type_}')  # Используем B- для начала
                else:
                    token_data["tags"].append(f'I-{token.ent_type_}')  # Используем I- для последующих
            else:
                token_data["tags"].append("O")  # Используем "O" для несущностей

        result.append(token_data)


    # Save token data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


convert_data(lines, file_res)