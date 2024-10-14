import spacy


# Загрузка модели spaCy для русского языка
nlp = spacy.load("ru_core_news_lg", exclude=['lemmatizer',])

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


# Инициализация лемматизатора
import pymorphy3
morph = pymorphy3.MorphAnalyzer()


# Печать списков в столбец
def print_list(list, label = None):
    if label:
        print(f'{label}:')

    # Если список пуст
    if not list or list == []:
        print('\tСписок пуст\n')
        return
    else:
        for item in list:
            print(f'\t{item}')
    print()