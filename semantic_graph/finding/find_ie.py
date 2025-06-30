import re
import json

from pymorphy3 import MorphAnalyzer

# Инициализируем лемматизатор
morph = MorphAnalyzer()

def lemmatize_words(words):
    return [morph.parse(word)[0].normal_form for word in words]

def find_words_with_suffixes(file_path, output_path):
    # Список суффиксов для поиска
    suffixes = ["ий"]

    # Формируем регулярное выражение для поиска полных слов с указанными суффиксами
    suffixes_pattern = '|'.join([re.escape(suffix) for suffix in suffixes])
    pattern = rf'\b\w*(?:{suffixes_pattern})\b'
    
    # Чтение JSON-файла и извлечение слов из него
    with open('combined_dict_word_1.json', 'r', encoding='utf-8-sig') as f:
        data = json.load(f)['noun']
    
    # Находим все слова, заканчивающиеся на указанные суффиксы
    find = set()
    for word in data:
        if re.search(pattern, word, re.IGNORECASE):
            find.add(word)
    
    # Лемматизируем слова
    # lemmatized_words = lemmatize_words(words_with_suffixes)
    
    # Удаляем дубликаты и сортируем результаты
    unique_lemmatized_words = sorted(find)
    
    # Записываем найденные слова в новый файл
    with open(output_file, 'w', encoding='utf-8') as file:
        for word in unique_lemmatized_words:
            file.write(f'{word}\n')

# Пример использования
input_file = 'one_corpus\\corpus_modified_2.txt'
output_file = 'find_side_e_in_dict.txt'
find_words_with_suffixes(input_file, output_file)