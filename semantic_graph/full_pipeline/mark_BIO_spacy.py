
# from constants import nlp

from spacy_load  import spacy_pipeline
from udpipe_load import ud_pipeline

# Формирование списка именованных сущностей из предложения
def filter_NER(tokens, tags):
    # Добавляем индекс i для каждого токена
    filtered_tokens_and_tags = [(i, token, tag) for i, (token, tag) in enumerate(zip(tokens, tags)) if tag != "O"]
    return filtered_tokens_and_tags

# # Поиск тега для заданного токена
# def get_tag_for_token(token, filtered_tokens_and_tags):
#     for tok, tag in filtered_tokens_and_tags:
#         if tok == token:
#             return tag
#     return None  # Возвращаем None, если токен не найден

# # Функция для получения зависимых слов с учетом исключений связей
# def get_dependents(word, tag, filtered_tokens_and_tags, level=1):
#     """
#     'conj'  -- связь однородности
#     'nmod'  -- дополнение
#     'amod'  -- прилагательное
#     'punct' -- пунктуация
#     'acl'   -- причатие
#     'nsubj' -- подлежащее
#     'case'  -- предлог
#     'cc'    -- союзы
#     """    
#     dependents = []

#     for child in word.children:
   
#         str_child = str(child)

#         exeption_link = []
#         if tag == 'mechanism':
#             exeption_link.append('nmod')
#             exeption_link.append('nsubj')


#         if  (level == 1 and child.dep_ in ('amod', 'nmod') and child.dep_ not in exeption_link)\
#         or  (level > 1 and child.dep_ in ('amod', 'nmod', 'cc', 'nsubj', 'conj', 'case')):
#             dependents.append((str_child, child.i))

#             # Рекурсивный вызов для получения зависимых слов зависимых слов
#             dependents.extend(get_dependents(child, tag, filtered_tokens_and_tags, level + 1))

#     return dependents

def bio_tagging(sequence):

    saved_tags = []
    converted_tags = sequence[:]  # Копия исходного списка для преобразований

    for i, tag in enumerate(sequence):
        if tag in {"O", "mechanism"}:
            # Удаление сохраненных тегов
            saved_tags.clear()
        elif tag == "side_e":
            # Преобразование всех сохраненных тегов в side_e
            for idx, saved_tag in saved_tags:
                converted_tags[idx] = "side_e"
            saved_tags.clear()  # Очищаем сохраненные теги после преобразования
        elif tag == "abbr" and saved_tags and saved_tags[-1][1] in {"side_e"}:
            # Преобразуем abbr в side_e, если предыдущий side_e
            converted_tags[i] = "side_e"
        else:
            # Сохраняем текущий тег и его индекс
            saved_tags.append((i, tag))

    bio_sequence = []
    previous_label = None

    for i, label in enumerate(converted_tags):
        if label == 'O':
            bio_sequence.append('O')
            previous_label = None 
        elif label != previous_label:
            bio_sequence.append(f'B-{label}')
            previous_label = label
        else:
            bio_sequence.append(f'I-{label}')

    return bio_sequence
    

def get_dependents(word, tag, filtered_tokens_and_tags, token_data, level=1, method="spacy"):
    """
    Получение зависимых слов с учетом исключений связей.
    :param word: Токен (spaCy/UDPipe).
    :param tag: Тег текущего токена.
    :param filtered_tokens_and_tags: Отфильтрованные токены с тегами.
    :param token_data: Список токенов (список словарей для UDPipe, spaCy токены для spaCy).
    :param level: Уровень вложенности зависимостей.
    :param method: Метод обработки ('spacy' или 'udpipe').
    """
    dependents = []

    # Определяем исключения
    exeption_link = []
    if tag == 'mechanism':
        exeption_link.extend(['nmod', 'nsubj'])

    # Для spaCy
    if method == "spacy":
        for child in word.children:
            if (
                (level == 1 and child.dep_ in ('amod', 'nmod') and child.dep_ not in exeption_link) or
                (level > 1 and child.dep_ in ('amod', 'nmod', 'cc', 'nsubj', 'conj', 'case'))
            ):
                dependents.append((str(child), child.i))
                dependents.extend(
                    get_dependents(child, tag, filtered_tokens_and_tags, token_data, level + 1, method)
                )

    # Для UDPipe
    elif method == "udpipe":
        for child in token_data:
            if child['head'] == word['id']:
                if (
                    (level == 1 and child['dep'] in ('amod', 'nmod') and child['dep'] not in exeption_link) or
                    (level > 1 and child['dep'] in ('amod', 'nmod', 'cc', 'nsubj', 'conj', 'case'))
                ):
                    dependents.append((child['text'], child['id'] - 1))
                    dependents.extend(
                        get_dependents(child, tag, filtered_tokens_and_tags, token_data, level + 1, method)
                    )

    return dependents


def find_series(doc, tokens, tags, method="spacy"):
    """
    Поиск зависимостей с использованием spaCy или UDPipe.
    :param doc: Документ (spaCy Doc или список токенов для UDPipe).
    :param tokens: Список токенов.
    :param tags: Список тегов.
    :param method: Метод обработки ('spacy' или 'udpipe').
    """
    # Поиск только слов с тегами
    filtered_tokens_and_tags = filter_NER(tokens, tags)

    # Получаем данные о токенах
    if method == "spacy":
        token_data = list(doc)
    elif method == "udpipe":
        token_data = [
            {"id": i + 1, "text": token, "dep": token_dep, "head": token_head}
            for i, (token, token_dep, token_head) in enumerate(zip(tokens, tags, [int(tag.split(":")[1]) if ":" in tag else 0 for tag in tags]))
        ]
    else:
        raise ValueError("Неизвестный метод обработки!")

    # Рекурсивный поиск зависимостей
    dependencies = {}
    for i, word, tag in filtered_tokens_and_tags:
        if method == "spacy":
            token = doc[i]
        elif method == "udpipe":
            token = next((t for t in token_data if t['id'] - 1 == i), None)
            if token is None:
                continue

        dependencies[(i, word)] = get_dependents(token, tag, filtered_tokens_and_tags, token_data, method=method)

    # Пример: переопределение тегов зависимых токенов на основе зависимостей
    for (head_index, head_token), dependents_list in dependencies.items():
        head_tag = tags[head_index]

        for dependent_token, dependent_index in dependents_list:
            tags[dependent_index] = head_tag  # Изменение тега зависимого слова

    bio_sequence = bio_tagging(tags)

    return bio_sequence
    