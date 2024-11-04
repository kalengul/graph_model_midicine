import os
from shutil import copy2

from bs4 import BeautifulSoup
import spacy

# Изменение токенизатора (определение исключений)
def load_nlp():

    # Загрузка модели spaCy для русского языка
    nlp = spacy.load("ru_core_news_lg", exclude=['lemmatizer',])

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
        'п/к',
        'др.',
        'пр.',
        'т.д.',
        'т.п.',
        'т.е.'
    ]

    # Добавляем исключения с помощью цикла
    for case in special_cases:
        nlp.tokenizer.add_special_case(case, [{'ORTH': case}])

    return nlp

nlp = load_nlp()

def svg2tuple(html_content):
    # Разбор HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Извлечение текста и тегов
    result = []



    # Обработка всех элементов внутри контейнера <div>
    for element in soup.div.children:
        
        # Если элемент <mark>
        if element.name == 'mark': 
            tag = element.find('span').get_text(strip=True)
            element.find('span').decompose()  # Удаляем <span>

            # Обрабатываем текст как список из одной строки
            doc = list(nlp.pipe([element.get_text(strip=True)]))[0]
            text_list = [token.text for token in doc]

            # Добавляем слова с их тегами
            for word in text_list:
                result.append((word, tag))

        # Если это обычный текст
        elif element.string:  
            words = element.string.strip()

            # Обрабатываем текст как список из одной строки
            doc = list(nlp.pipe([words]))[0]
            text_list = [token.text for token in doc]

            # Добавляем слова с тегом "O"
            for word in text_list:
                result.append((word, 'O'))
    
    return result

def compare_annotations(tokens_tags1, tokens_tags2):
    # print("tokens_tags1:", tokens_tags1)
    # print("tokens_tags2:", tokens_tags2)

    """Сравнивает два набора токенов и тегов и считает процент совпадений."""
    if len(tokens_tags1) != len(tokens_tags2):
        print(f"Ошибка: разные длины списков. ({len(tokens_tags1)}/{len(tokens_tags2)})")
        return 0
    
    mark_tokens = [(token, tag) for token, tag in  tokens_tags1 if tag != 'O']
    mark_token_O = [(token, tag) for token, tag in  tokens_tags1 if tag == 'O']
    
    total_mark = len(mark_tokens)
    total_mark_O = len(mark_token_O)
    total_all = len(tokens_tags1)

    matches_mark = sum(1    for    (token1, tag1),
                                   (token2, tag2)
                            in zip (tokens_tags1,
                                    tokens_tags2)
                            if      tag1 == tag2
                            and     tag1 != 'O'
                            and     tag2 != 'O'
                )
    
    matches_mark_O = sum(1    for    (token1, tag1),
                                (token2, tag2)
                        in zip (tokens_tags1,
                                tokens_tags2)
                        if      tag1 == tag2
                        and     tag1 == 'O'
                        and     tag2 == 'O'
            )
    
    matches_all = sum(1 for    (token1, tag1),
                                (token2, tag2)
                        in zip (tokens_tags1,
                                tokens_tags2)
                        if      tag1 == tag2
            )

    # Вычисляем процент совпадений
    # accuracy = (matches_mark / total_mark)* (matches_all / total_all) * 100
    # accuracy = (matches_mark / total_mark) * 100
    # accuracy = (matches_all / total_all) * 100
    # accuracy = (matches_mark / total_mark) * (matches_mark_O / total_mark_O) * 100
    accuracy = (matches_mark / total_mark) * (matches_mark_O / total_mark_O) * (matches_all / total_all) * 100
    return accuracy

def get_files_in_directory(directory):
    """Возвращает список всех файлов в указанной директории."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

# Извечение и преобразование эталона
with open('standart_mark.svg', 'r', encoding='utf-8') as file:
    reference_tokens_tags = file.read()
standart_mark = svg2tuple(reference_tokens_tags)

# Список для хранения результатов сравнения
accuracy_list = []

# Получаем все файлы в папке "results"
result_files = get_files_in_directory('results')

# Сравнение каждого файла с эталоном
for result_file in result_files:
    with open(result_file, 'r', encoding='utf-8') as file:
        result_content = file.read()

    # Извлечение токенов и тегов из текущего файла
    print("file", result_file)
    result_tokens_tags = svg2tuple(result_content)

    # Вычисление процента совпадений
    accuracy = compare_annotations(standart_mark, result_tokens_tags)
    accuracy_list.append((result_file, accuracy))

# Сортируем по убыванию точности и берем топ-30
accuracy_list.sort(key=lambda x: x[1], reverse=True)
top_30 = accuracy_list[:15]

for item in top_30:
    print(item)

# Копируем и переименовываем топ-30 файлов в папку "best"
for index, (file, accuracy) in enumerate(top_30, start=1):
    # Формируем новое имя файла с учетом ранга
    new_filename = f"{index:02d}_{os.path.basename(file)}"
    new_file_path = os.path.join('best', new_filename)
    # Копируем файл с новым именем
    copy2(file, new_file_path)

print("Топ-15 файлов успешно сохранены в папку 'best'.")