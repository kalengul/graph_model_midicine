import spacy

# Загрузите модель spaCy для русского языка
nlp = spacy.load("ru_core_news_lg")

import spacy

# Формирование списка именованных сущностей из предложения
def filter_NER(tokens, tags):
    filtered_tokens_and_tags = [(token, tag) for token, tag in zip(tokens, tags) if tag != "O"]
    return filtered_tokens_and_tags

# Поиск тега для заданного токена
def get_tag_for_token(token, filtered_tokens_and_tags):
    for tok, tag in filtered_tokens_and_tags:
        if tok == token:
            return tag
    return None  # Возвращаем None, если токен не найден

# Поиск заданного слова
def find_token(target_word, doc):
    target_token = None

    # Поиск токена, соответствующего заданному слову
    for token in doc:
        if token.text == target_word:
            target_token = token
            break

    return target_token

# Функция для получения зависимых слов с учетом исключений связей
def get_dependents(word, tag, filtered_tokens_and_tags, level=1):
    """
    'conj'  -- перечисление
    'nmod'  -- дополнение, отвечает на вопрос "чего?"
    'punct' -- пунктуация
    'acl'   -- причатие
    :::     -- дополнить остальные
    """
    
    dependents = []
    
    for child in word.children:

        str_child = str(child)
        exeption_link = ['conj', 'punct', 'parataxis', 'mark', 'advcl', 'fixed', 'acl']

        if tag == 'mechanism':
            exeption_link.append('nmod')
            exeption_link.append('obj')
            exeption_link.append('nsubj')
            exeption_link.append('obl')
            exeption_link.append('nsubj:pass')     
            exeption_link.append('advmod')
            exeption_link.append('iobj')
            exeption_link.append('case')

        if tag in ('side_e', 'noun', 'prepar', 'abbr'):
            exeption_link.append('acl:relcl')

        # Если механизм "залезает" на другую сущность не механизм
        if  any(token == str_child for token, _ in filtered_tokens_and_tags)\
            and \
            tag == 'mechanism':
            return dependents

        # На первом уровне исключить запятые, точки и перечисления
        # На первом и последующих уровнях исключить причастия
        if (((level == 1 and child.dep_ not in exeption_link) or (level > 1)) \
            and str_child not in ('и')):
            dependents.append(str_child)

            # Рекурсивный вызов для получения зависимых слов зависимых слов
            dependents.extend(get_dependents(child, tag, filtered_tokens_and_tags, level + 1))

    return dependents

# Определение последовательности
def bio_tagging(sequence):
    bio_sequence = []
    previous_label = None

    for i, label in enumerate(sequence):
        if label == 'O':
            bio_sequence.append('O')
            previous_label = None
        elif label != previous_label:
            bio_sequence.append(f'B-{label}')
            previous_label = label
        else:
            bio_sequence.append(f'I-{label}')
    
    return bio_sequence

def find_series(doc, tokens, tags):

    filtered_tokens_and_tags = filter_NER(tokens, tags)

    # Рекурсивный поиск зависимостей
    dependencies = {}
    for word, tag in filtered_tokens_and_tags:
        token = find_token(word, doc)
        dependencies[str(token)] = get_dependents(token, tag, filtered_tokens_and_tags)


    # print(dependencies)

    
    # Создаем словарь, чтобы быстро находить индекс слова по его значению
    token_to_index = {token:index  for index, token in enumerate(tokens)}

    # Проходим по зависимостям и меняем теги зависимых слов
    for head, dependents in dependencies.items():
        head_index = token_to_index[head]
        head_tag = tags[head_index]
        for dependent in dependents:
            dependent_index = token_to_index[dependent]
            tags[dependent_index] = head_tag

    bio_sequence = bio_tagging(tags)

    # print(tokens)
    # print(tags)
    # print(bio_sequence)

    # print()

    return bio_sequence
    