import spacy

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
        'п/к',
        'др.',
        'пр.',
        'т.д.',
        'т.п.',
        'т.е.'
    ]

    # Добавляем исключения с помощью цикла
    for case in special_cases:
        tokenizer.add_special_case(case, [{'ORTH': case}])

    return tokenizer

# Загрузка модели spaCy для русского языка
spacy_pipeline = spacy.load("ru_core_news_lg", exclude=['lemmatizer',])

spacy_pipeline.tokenizer = custom_tokenizer(spacy_pipeline)

