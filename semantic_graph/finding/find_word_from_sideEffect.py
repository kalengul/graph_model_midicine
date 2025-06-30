import json
import pandas as pd
import pymorphy3
from nltk.corpus import stopwords
from nltk import word_tokenize

import sys
sys.path.append("")
from my_lib.lemmatize import lemmatize_sentence, load_punkt, load_stopwords

# Инициализация pymorphy3
morph = pymorphy3.MorphAnalyzer()
russian_stopwords = load_stopwords()

# Дополнительные стоп-слова
additional_stopwords = {'и', 'а', 'но', 'или', 'да', 'если', 'то', 'и/или'}
russian_stopwords.update(additional_stopwords)

# Функция для определения части речи и лемматизации
def get_word_type_and_lemma(word):
    parsed = morph.parse(word)[0]
    pos = parsed.tag.POS
    lemma = parsed.normal_form if parsed.is_known else word  # Если слово неизвестно, оставить его в исходной форме
    
    if lemma in russian_stopwords:
        return None, None
    
    if pos == 'INFN' or pos == 'VERB':
        return 'verb', lemma
    elif pos == 'NOUN':
        return 'noun', lemma
    elif pos == 'ADJF' or pos == 'ADJS':
        return 'adjective', lemma
    elif pos == 'PRTF' or pos == 'PRTS':
        return 'participle', lemma
    elif pos == 'GRND':
        return 'gerund', lemma
    else:
        return None, None

# Чтение JSON файла
with open('json_files\\Dictionary.json', 'r', encoding='utf-8-sig') as file:
    data = json.load(file)

# Извлечение и обработка строк
unique_words = {'verb': set(), 'noun': set(), 'adjective': set(), 'participle': set(), 'gerund': set()}

for item in data['SideEffects']:
    words = word_tokenize(item, language='russian')
    for word in words:
        word_type, lemma = get_word_type_and_lemma(word)
        if word_type and lemma:
            unique_words[word_type].add(lemma)

# Преобразование множеств в отсортированные списки
sorted_words = {
    'verb': sorted(unique_words['verb']),
    'noun': sorted(unique_words['noun']),
    'adjective': sorted(unique_words['adjective']),
    'participle': sorted(unique_words['participle']),
    'gerund': sorted(unique_words['gerund'])
}

# Создание DataFrame и запись в Excel
df = pd.DataFrame({
    'verbs': pd.Series(sorted_words['verb']),
    'nouns': pd.Series(sorted_words['noun']),
    'adjectives': pd.Series(sorted_words['adjective']),
    'participles': pd.Series(sorted_words['participle']),
    'gerunds': pd.Series(sorted_words['gerund'])
})

df.to_excel('output.xlsx', index=False)