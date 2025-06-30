import re

from pymorphy3 import MorphAnalyzer

# Инициализируем лемматизатор
morph = MorphAnalyzer()

def lemmatize_words(words):
    return [morph.parse(word)[0].normal_form for word in words]

def find_words_with_suffixes(file_path, output_path):
    # Список суффиксов для поиска
    suffixes = [
        "ид", "ол", "ин", "он", "ан", "ат", "ен", "ик", "ант", "ил",
        "иды", "олы", "ины", "оны", "аны", "аты", "ены", "икы", "анты", "илы",
        "ивов", "олов", "инов", "онов", "анов", "атов", "енов", "иков", "антов", "илов",
        "ида", "ола", "ина", "она", "ана", "ата", "ена", "ика", "анта", "ила",
        "иду", "олу", "ину", "ону", "ану", "ату", "ену", "ику", "анту", "илу",
        "иде", "оле", "ине", "оне", "ане", "ате", "ене", "ике", "анте", "иле",
        "идом", "олом", "ином", "оном", "аном", "атом", "еном", "иком", "антом", "илом"
    ]

    # Формируем регулярное выражение для поиска полных слов с указанными суффиксами
    suffixes_pattern = '|'.join([re.escape(suffix) for suffix in suffixes])
    pattern = rf'\b\w*(?:{suffixes_pattern})\b'
    
    # Читаем текст из файла
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Находим все слова, заканчивающиеся на указанные суффиксы
    words_with_suffixes = re.findall(pattern, text, re.IGNORECASE)
    
    # Лемматизируем слова
    lemmatized_words = lemmatize_words(words_with_suffixes)
    
    # Удаляем дубликаты и сортируем результаты
    unique_lemmatized_words = sorted(set(lemmatized_words))
    
    # Записываем найденные слова в новый файл
    with open(output_file, 'w', encoding='utf-8') as file:
        for word in unique_lemmatized_words:
            file.write(f'{word}\n')

# Пример использования
input_file = 'one_corpus\\corpus_modified_2.txt'
output_file = 'preparates.txt'
find_words_with_suffixes(input_file, output_file)