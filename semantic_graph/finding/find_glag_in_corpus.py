import json
import re
import pymorphy3

morph = pymorphy3.MorphAnalyzer()

def is_verb(word, morph):
    # Определение глагола с помощью pymorphy3
    parsed_word = morph.parse(word)[0]
    return 'VERB' in parsed_word.tag or 'INFN' in parsed_word.tag

# Загрузка данных из JSON
with open('combined_dict_word_1.json', 'r', encoding='utf-8') as f:
    verbs_from_json = json.load(f)['prilag']

with open('one_corpus\\corpus_modified_2.txt', 'r', encoding='utf-8') as f:
    text = f.read()

def is_need_word(word, morph):
    # Определение глагола с помощью pymorphy3
    parsed_word = morph.parse(word)[0]
    return 'ADJF' in parsed_word.tag or 'ADJS' in parsed_word.tag
    # return 'VERB' in parsed_word.tag or 'INFN' in parsed_word.tag

def normalize(word):
    word = morph.parse(word)[0].normal_form

    # if word.endswith('ся'):
    #     return word[:-2]
    return word
    

def get_unique_verbs(text):
    # re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
    # # Регулярное выражение для разделения строки по пробелам и выделения нужных символов в отдельные элементы
    # pattern = r'\s+|([",:;(){}[\]])'
    # # re.split для разделения строки
    # split_elements = re.split(pattern, text)
    # # Удаление пустых строк из списка
    # words = [elem for elem in split_elements if elem is not None and elem != ""]

    # # Удаление точки из конца последнего элемента
    # if words and words[-1].endswith('.'):
    #     words[-1] = words[-1][:-1]

    words = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)

    unique_verbs = {normalize(word) for word in words if is_need_word(word, morph)}

    return unique_verbs

unique_verbs = get_unique_verbs(text)
resulting_verbs = unique_verbs - set(verbs_from_json)

with open('prilag_in_corpus.txt', 'w', encoding='utf-8') as f:
    for glag in resulting_verbs:
        f.write(glag + '\n')