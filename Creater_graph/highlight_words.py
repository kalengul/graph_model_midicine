import spacy
import uuid

# Загружаем модель spaCy для русского языка
nlp = spacy.load("ru_core_news_lg")

# Определяет диапазоны последовательностей BIO и соответствующие токены
def get_ner_tokens(tokens, tags):
    ranges = []
    start = None
    current_tag = None

    for i, (token, tag) in enumerate(zip(tokens, tags)):
        if tag.startswith("B-"):
            if start is not None:
                ranges.append((str(uuid.uuid4()), start, i - 1, tokens[start:i], current_tag))
            start = i
            current_tag = tag.split('-')[-1]
        elif tag.startswith("I-") and start is not None:
            continue
        elif tag.startswith("O") and start is not None:
            ranges.append((str(uuid.uuid4()), start, i - 1, tokens[start:i], current_tag))
            start = None
            current_tag = None

    if start is not None:
        ranges.append((str(uuid.uuid4()), start, len(tags) - 1, tokens[start:], current_tag))
    
    return ranges


# Поиск связей с механизмом
def find_mechanism_connections(doc, ner_tokens):
    connections = []

    # Создание словаря для быстрого доступа к токенам по диапазонам
    bio_sequences_dict = { (start, end): (uid, tokens, label) for uid, start, end, tokens, label in ner_tokens}

    # По индексу определяет словосочетания 
    def find_tokens_in_range(index, sequences_dict):
        for start, end in sequences_dict.keys():
            if start <= index <= end:
                uid, tokens, label = sequences_dict[(start, end)]
                return uid, tokens, start, end, label
        return None, None, None, None, None

    # Нахождение все токены с меткой 'mechanism'
    mechanism_tokens = [token for token in doc if token._.custom_tag in {"B-mechanism", "I-mechanism"}]

    for mechanism in mechanism_tokens:
        uid_mech, mechanism_series, start_mech, end_mech, label_mech = find_tokens_in_range(mechanism.i, bio_sequences_dict)

        if not mechanism_series:
            continue

        related_tokens = []

        # Функция для проверки зависимости nmod и conj
        def is_related_token(token, mechanism):
            valid_tags = {"B-side_e", "I-side_e", "B-noun", "I-noun", "B-prepar", "I-prepar", "B-abbr", "I-abbr"}
            return token._.custom_tag in valid_tags and token.head == mechanism

        # Поиск связанных и conj-связанных токенов
        related_tokens = [(token, token.i) for token in doc if is_related_token(token, mechanism)]
        conj_related_tokens = [(token, token.i) for token in doc for rel_token, _ in related_tokens if token.dep_ == "conj" and token.head == rel_token]

        # Объединяем связанные токены
        all_related_tokens = related_tokens + conj_related_tokens

        # Поиск серий для всех связанных токенов
        if all_related_tokens:
            for _, related_index in all_related_tokens:
                uid_related, related_series, start, end, label = find_tokens_in_range(related_index, bio_sequences_dict)
                if related_series:
                    connections.append(((uid_mech, start_mech, end_mech, mechanism_series, label_mech),
                                        (uid_related, start, end, related_series, label)))

    return connections

# Определение не связанных слов
def find_not_connections(data, connections):
    
    # Извлечение связанных слов с механизмом и механизмов
    linked_phrases =  [connection[0][3] for connection in connections]
    linked_phrases += [connection[1][3] for connection in connections]
    
    # Сохранение индексов элементов, которые нужно исключить (механизмы и связанные с ними)
    exclude_indices = set()

    # Поиск элементов, связанных с механизмом через словосочетания
    for item in data:
        # Проверяем совпадение словосочетаний
        if any(word in item[3] for phrase in linked_phrases for word in phrase):
            exclude_indices.add(data.index(item))
        
    # Формируем результат: все элементы, которые не входят в exclude_indices
    result = [item for i, item in enumerate(data) if i not in exclude_indices]

    return(result)

# Печать списков в столбец
def print_list(list, label = None):
    if label:
        print(label)

    for item in list:
        print(item)
    
    print()

def find_connections(tokens, tags):
    # Создание текста для анализа
    text = " ".join(tokens)
    doc = nlp(text)

    # Привязка кастомных тегов к токенам в doc
    for token, tag in zip(doc, tags):
        token.set_extension("custom_tag", default=False, force=True)
        token._.custom_tag = tag

    # Определение диапазонов для BIO последовательностей
    ner_tokens = get_ner_tokens(tokens, tags)
    # print_list(ner_tokens, label = "Исходный список NER")

    # Поиск связей и вывод BIO последовательностей
    connections = find_mechanism_connections(doc, ner_tokens)
    # print_list(connections, label = "Связанные токены")

    # Исключение не связанных словосочетаний
    not_connections = find_not_connections(ner_tokens, connections)
    # print_list(not_connections, label = "Не связанные токены")

    return ner_tokens, connections, not_connections
