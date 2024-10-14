import json
import time

import concurrent.futures

from mark_BIO_spacy import find_series
from constants import nlp, morph

# Путь к входному и выходному файлам'
diction_file = 'full_pipeline\\combined_dict_word_3.json'

# Функция для удаления начальных и конечных кавычек
def remove_quotes(s):
    if isinstance(s, str):
        # Удаление начальных и конечных кавычек
        s = s.strip('"\'«»')
    return s

# Загрузка данных из JSON
with open(diction_file, 'r', encoding='utf-8') as f:
    tags_dict = json.load(f)

# Привести слова в нормальную форму
def preprocess_text(words):
    normalized_words = []
    for word in words:
        word = remove_quotes(word)                      # Убрать кавычки, если имеются
        normal_form = morph.parse(word)[0].normal_form  # Нормализация

        # Проверка заканчивается на "ся"
        if normal_form.endswith('ся'):
            normal_form = normal_form[:-2]

        normalized_words.append(normal_form)
    
    return normalized_words

# Определить для слова тег
def get_tag(token, pos):
    
    # Если знак препинания, наречие, прилагательное
    if pos in ('PUNCT', 'ADV', 'ADJ'):
        return "O"  
    
    if pos in ("SYM"):
        return "sym"
        
    # Поиск по словарю
    for tag, words in tags_dict.items():

        if tag != 'noun_ie':

            if token in words:
                return tag
        
    # Если глагол
    if pos in ('VERB'):
        return "mechanism" 
    
    # Если аббревиатура
    if pos in ("PROPN"):
        return "abbr"
    
    return "O"  # Если токен не найден в словаре

# Корректировка "не"
def copy_tag_for_ne(tokens, tags):
    i = 0
    while i < len(tokens) - 1:
        if tokens[i].lower() == "не":
            tags[i] = tags[i + 1]
        i += 1

    return tags

def process_line(line):

    # Токенизация и получение частей речи
    tokens = [token.text for token in line]
    tokens_pos = [token.pos_ for token in line]

    # Нормализация токенов
    normalized_words = preprocess_text(tokens)

    # Тегирование слов
    tags = [get_tag(token, pos) for token, pos in zip(normalized_words, tokens_pos)]

    # Учёт "не" перед словом
    tags = copy_tag_for_ne(tokens, tags)

    # Нахождение серии (поиск зависимых слов от главного)
    tags = find_series(line, tokens, tags)

    return {
        "tokens": tokens,
        "tags": tags
    }


# Подача на вход строк (предложений)
# На выходе размеченные данные
def mark_lines(lines):
    data = []

    # Убедись, что многопоточность работает только при запуске основного скрипта
    if __name__ == "__main__":
        docs = list(nlp.pipe(lines, n_process=4))
    else:
        docs = list(nlp.pipe(lines))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for doc in docs:
            future = executor.submit(process_line, doc)
            futures.append(future)

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            data.append(future.result())
            print('step', i)

    return data