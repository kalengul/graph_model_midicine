import json
import re

import pymorphy3

# Открытие json файла
with open('Dictionary.json', 'r', encoding='utf-8-sig') as file:
    data = json.load(file)

# Чтение текстового файла
with open('one_corpus\\corpus_full.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# Удаление фрагментов
text = re.sub(r' \(см\..*?\)', '', text)                                    # "(см. ... )"
text = re.sub(r' \(исследование.*?\)', '', text)                            # "(исследование ... )"
text = re.sub(r'^Таблица.*\d+$', '', text, flags=re.MULTILINE)              # "Таблица n"
text = re.sub(r'^RxList\.com.*$', '', text, flags=re.MULTILINE)             # "RxList.com ..."
text = re.sub(r',? показаны в таблице \d+', '', text)                       # ", показаны в таблице n"
text = re.sub(r'\(таблица \d+\)', '', text)                                 # "(таблица n)"

# text = re.sub(r'\(от \d+ до \d+ лет\)', '', text)                         # "(от n до m лет)"
text = re.sub(r'\(\s*[^)]*?\s+лет\)', '', text)                             # ( ... лет)"

text = re.sub(r'\(\d+(?:,\d+)? или \d+(?:,\d+)? мг/сут\)', '', text)        # "(n или m мг/сут)"
text = re.sub(r'\(\d+ мг/кг/сут\)', '', text)                               # "(n мг/кг/сут)"

text = re.sub(r'\(около \d+%\)', '', text)                                  # "(около <число>%)"
text = re.sub(r' \(\d+(?:,\d+)?%\)', '', text)                              # "(n%)"
text = re.sub(r'\(\d+(?:,\d+)?–\d+(?:,\d+)?%\)', '', text)                  # "(n-m%)"

text = re.sub(r'Результаты представлены в таблице \d+.', '', text)          # "Результаты представлены в таблице n"
text = re.sub(r'\(например, [^)]*?\)', '', text)                            # "(например, ... )"

# # Замена "<число>%" на "<число> процентов"
# text = re.sub(r'(\d+)%', r'\1 процентов', text)

# Замена сокращений на целые слова
redudeses_dict = data["Reduses"]
for key, value in redudeses_dict.items():
    if isinstance(value, list):
        for synonym in value:
            # Экранирование специальных символов
            pattern = re.escape(synonym)
            text = re.sub(pattern, key, text)
    elif isinstance(value, str):
        # Экранирование специальных символов
        pattern = re.escape(value)
        text = re.sub(pattern, key, text)


# Инициализация морфологического анализатора
morph = pymorphy3.MorphAnalyzer()

# Функция для замены слова на ключ с сохранением прилегающих символов
def replace_word_with_key(word, key, prefix, suffix):
    print(f"{prefix + word + suffix}  => {prefix + key + suffix}")
    return prefix + key + suffix

# Функция для лемматизации и замены слов на ключи
def lemmatize_and_replace(text, synonyms_dict):
    # Разделение текста на слова и пробелы
    words = re.split(r'(\s+)', text)
    new_words = []

    for word in words:
        # Проверка, является ли слово буквенным
        if re.match(r'\w+', word):
            # Отделение прилегающих символов
            prefix = re.match(r'^[^\w]+', word)
            suffix = re.search(r'[^\w]+$', word)
            
            if prefix:
                prefix = prefix.group()
                word = word[len(prefix):]
            else:
                prefix = ''
            
            if suffix:
                suffix = suffix.group()
                word = word[:-len(suffix)]
            else:
                suffix = ''

            # Понижение регистра и лемматизация слова
            lemma = morph.parse(word.lower())[0].normal_form

            # Замена слова на ключ, если лемма есть в списке синонимов или соответствует строке
            replaced = False
            for key, value in synonyms_dict.items():
                key_lower = key.lower()
                if isinstance(value, list):
                    if lemma in map(str.lower, value):
                        new_words.append(replace_word_with_key(word, key_lower, prefix, suffix))
                        replaced = True
                        break
                elif isinstance(value, str):
                    if lemma == value.lower():
                        new_words.append(replace_word_with_key(word, key_lower, prefix, suffix))
                        replaced = True
                        break

            # Если замена не произошла, возвращаем слово с прилегающими символами
            if not replaced:
                new_words.append(prefix + word + suffix)
        else:
            # Если это не слово, просто добавляем его
            new_words.append(word)

    return ''.join(new_words)

# Замена слов на ключи
synonyms_dict = data["Synonyms"]
text = lemmatize_and_replace(text, synonyms_dict)


# Удаление \n в конце строки
# text = re.sub(r'\n$', '', text, flags=re.MULTILINE)

# Сохранение измененного текста в новый файл
with open('one_corpus\\corpus_modified.txt', 'w', encoding='utf-8') as file:
    file.write(text)

# print("Замены выполнены и сохранены в 'corpus_modified.txt'.")




