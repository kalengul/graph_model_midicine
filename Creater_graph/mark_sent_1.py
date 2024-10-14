import json
import pymorphy3

import concurrent.futures


from mark_BIO_spacy import find_series
import spacy

# Загрузка модели для русского языка
nlp = spacy.load("ru_core_news_lg")

# Путь к входному и выходному файлам
diction_file = 'combined_dict_word_3.json'
# input_file = 'one_corpus\\corpus_modified_3.txt'
# output_file = 'train_model\\mark_sent_3.json'

# Изменение токенизатора (определение исключений)
def custom_tokenizer(nlp):
    # Получаем существующий токенизатор
    tokenizer = nlp.tokenizer

    # Список исключений
    special_cases = [
        'и/или',
        'мг/кг/сут',
        'мл/кг/ч',
        'в/в',
        'в/м',
        'T1/2',
        'л/кг',
        'мкг/мл',
        'мг/мл',
        'нг/мл',
        'кг/сут',
        'мкг·ч/мл',
        'мг/кг',
        'мг/м2',
        'мг/сут',
        'мл/кг',
        'мл/мин',
        'л/мин',
        'ммоль/л',
        'мг/дл',
        'г/дл',
        'п/к'
    ]

    # Добавляем исключения с помощью цикла
    for case in special_cases:
        tokenizer.add_special_case(case, [{'ORTH': case}])

    return tokenizer

nlp.tokenizer = custom_tokenizer(nlp)

# Инициализация морфологического анализатора
morph = pymorphy3.MorphAnalyzer()

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
        
    # Если аббревиатура
    if pos in ("PROPN"):
        return "noun"
        # return "abbr"
    
    # Поиск по словарю
    for tag, words in tags_dict.items():
        if token in words:
            return tag
        
    # Если глагол
    if pos in ('VERB'):
        return "mechanism" 
    
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
    doc = nlp(line.strip())
    tokens = [token.text for token in doc]
    tokens_pos = [token.pos_ for token in doc]

    # Нормализация токенов
    normalized_words = preprocess_text(tokens)

    # Тегирование слов
    tags = [get_tag(token, pos) for token, pos in zip(normalized_words, tokens_pos)]

    # Учёт "не"
    tags = copy_tag_for_ne(tokens, tags)

    # Нахождение серии
    tags = find_series(doc, tokens, tags)

    return {
        "tokens": tokens,
        "tags": tags
    }


# Подача на вход строк (предложений)
# На выходе размеченные данные
def mark_lines(lines):
    data = []
        
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for line in lines:
            future = executor.submit(process_line, line)
            futures.append(future)

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            data.append(future.result())

    return data


# Запуск обработки
# mark_lines(input_file, output_file)
