
# from constants import nlp

# Формирование списка именованных сущностей из предложения
def filter_NER(tokens, tags):
    # Добавляем индекс i для каждого токена
    filtered_tokens_and_tags = [(i, token, tag) for i, (token, tag) in enumerate(zip(tokens, tags)) if tag != "O"]
    return filtered_tokens_and_tags

# Поиск тега для заданного токена
def get_tag_for_token(token, filtered_tokens_and_tags):
    for tok, tag in filtered_tokens_and_tags:
        if tok == token:
            return tag
    return None  # Возвращаем None, если токен не найден

# Функция для получения зависимых слов с учетом исключений связей
def get_dependents(word, tag, filtered_tokens_and_tags, level=1):
    """
    'conj'  -- связь однородности
    'nmod'  -- дополнение
    'amod'  -- прилагательное
    'punct' -- пунктуация
    'acl'   -- причатие
    'nsubj' -- подлежащее
    'case'  -- предлог
    'cc'    -- союзы
    """    
    dependents = []

    for child in word.children:
   
        str_child = str(child)

        exeption_link = []
        if tag == 'mechanism':
            exeption_link.append('nmod')
            exeption_link.append('nsubj')


        if  (level == 1 and child.dep_ in ('amod', 'nmod') and child.dep_ not in exeption_link)\
        or  (level > 1 and child.dep_ in ('amod', 'nmod', 'cc', 'nsubj', 'conj', 'case')):
            dependents.append((str_child, child.i))

            # Рекурсивный вызов для получения зависимых слов зависимых слов
            dependents.extend(get_dependents(child, tag, filtered_tokens_and_tags, level + 1))

    return dependents


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
    

def find_series(doc, tokens, tags):

    # Поиск только слов с тегами
    filtered_tokens_and_tags = filter_NER(tokens, tags)

    # Рекурсивный поиск зависимостей
    dependencies = {}
    for i, word, tag in filtered_tokens_and_tags:
        token = doc[i]

        dependencies[(token.i, str(token))] = get_dependents(token, tag, filtered_tokens_and_tags)
    
    # Пример: переопределение тегов зависимых токенов на основе зависимостей
    for (head_index, head_token), dependents_list in dependencies.items():
        # Получаем индекс головного слова и его тег
        head_tag = tags[head_index]

        # Обходим список зависимых слов для данного головного слова
        for dependent_token, dependent_index in dependents_list:
            tags[dependent_index] = head_tag  # Изменение тега зависимого слова

    bio_sequence = bio_tagging(tags)

    return bio_sequence
    