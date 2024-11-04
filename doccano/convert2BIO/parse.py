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
file_3 = "jsons\\data_1.jsonl"
# file_4 = "jsons\\data_edit_1.jsonl"

file_log = 'log.txt'  # Имя файла для записи

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


def split_data(file_path, train_ratio=0.8):
    # Читаем все данные из файла
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Перемешиваем данные для случайного распределения
    random.shuffle(lines)

    # Рассчитываем количество тренировочных, валидационных и тестировочных данных
    train_size = int(len(lines) * train_ratio)

    # Разделяем данные на тренировочные, валидационные и тестировочные
    train_data = lines[:train_size]
    val_data = lines[train_size:]

    return train_data, val_data

def convert_data(lines, nlp):
    db = DocBin()  # create a DocBin object

    for line in lines:
        data = json.loads(line)

        # Текст
        id = data["id"]
        text = data["text"]
        doc = nlp.make_doc(text)

        # Сущности
        entities = data.get("entities", [])
        ents = []

        # Оптимизированная запись данных в файл
        tokens_text = "Token: " + " ".join(f"'{token.text}'" for token in doc) + "\n"
        write_add(file_log, tokens_text)

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

            if span is None:
                write_add(file_log, f"NONE: id:{id_w}, {start}-{end} '{text[start:end]}'\n")
            # Проверяем, что span был создан успешно
            else:
                ents.append(span)

        # Сортировка списка ents по началу каждого span (start_char)
        ents.sort(key=lambda span: span.start_char)

        for ent in ents:
            write_add(file_log, f"span: id:{id}, {ent.start_char}-{ent.end_char} {ent}\n")
        
        # Назначаем сущности документу
        doc.ents = ents
        db.add(doc)

    return db

# Разделение данных
train_data, val_data = split_data(file_3, train_ratio=0.8)

# Конвертация данных в DocBin формат
train_db = convert_data(train_data, nlp)
val_db = convert_data(val_data, nlp)

# Сохранение в файлы
train_db.to_disk(f"datasets\\train.spacy")
val_db.to_disk(f"datasets\\val.spacy")

print("Данные успешно разделены и сохранены.")
