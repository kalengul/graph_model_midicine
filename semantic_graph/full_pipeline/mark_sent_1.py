import json
import time
import concurrent.futures

from mark_BIO_spacy import find_series

from spacy_load  import spacy_pipeline
from udpipe_load import ud_pipeline

# Инициализация лемматизатора
import pymorphy3
morph = pymorphy3.MorphAnalyzer()

# Путь к входному и выходному файлам
# diction_file = 'combined_dict_word_3.json'
diction_file = 'full_pipeline\\data\\combined_dict_word_3.json'
# input_file = 'one_corpus\\corpus_modified_3.txt'
# output_file = 'train_model\\mark_sent_3.json'

# Функция для удаления начальных и конечных кавычек
def remove_quotes(s):
    if isinstance(s, str):
        # Удаление начальных и конечных кавычек
        s = s.strip('"\'«»')
    return s

# Загрузка данных из JSON
with open(diction_file, 'r', encoding='utf-8') as f:
    tags_dict = json.load(f)

# Привести слова в нормальную форму
def preprocess_text(words):
    normalized_words = []
    for word in words:
        word = remove_quotes(word)                      # Убрать кавычки, если имеются
        normal_form = morph.parse(word)[0].normal_form  # Нормализация

        # Проверка заканчивается на "ся"
        if normal_form.endswith('ся'):
            normal_form = normal_form[:-2]

        normalized_words.append(normal_form)
    
    return normalized_words

# Токенизация и получение частей речи с помощью spaCy
def process_with_spacy(line):
    tokens = [token.text for token in line]
    tokens_pos = [token.pos_ for token in line]
    return tokens, tokens_pos

# Токенизация и получение частей речи с помощью UDPipe
def process_with_udpipe(line):
    processed = ud_pipeline.process(line)
    tokens, tokens_pos = [], []

    for line in processed.split("\n"):
        if not line.startswith("#") and line.strip():
            columns = line.split("\t")
            tokens.append(columns[1])       # Слово
            tokens_pos.append(columns[3])   # Часть речи (UPOS)
    
    return tokens, tokens_pos

# Определить для слова тег
def get_tag(token, pos):
    
    # Если знак препинания, наречие, прилагательное
    if pos in ('PUNCT', 'ADV', 'ADJ'):
        return "O"  
    
    if pos in ("SYM"):
        return "sym"
        
    # Поиск по словарю
    for tag, words in tags_dict.items():
        if tag == 'noun_ie':
            continue
        if token in words:
            return tag
        
    # Если глагол
    if pos in ('VERB'):
        return "mechanism" 
    
    # Если аббревиатура
    if pos in ("PROPN"):
        return "abbr"
    
    return "O"  # Если токен не найден в словаре

# Корректировка "не"
def copy_tag_for_ne(tokens, tags):
    i = 0
    while i < len(tokens) - 1:
        if tokens[i].lower() == "не":
            tags[i] = tags[i + 1]
        i += 1

    return tags

# Основная функция обработки строки
def process_line(line, method="spacy"):
    if method == "spacy":
        tokens, tokens_pos = process_with_spacy(line)
    elif method == "udpipe":
        tokens, tokens_pos = process_with_udpipe(line)
    else:
        raise ValueError(f"Неизвестный метод: {method}")

    # Нормализация токенов
    normalized_words = preprocess_text(tokens)

    # Тегирование слов
    tags = [get_tag(token, pos) for token, pos in zip(normalized_words, tokens_pos)]

    # Учёт "не" перед словом
    tags = copy_tag_for_ne(tokens, tags)

    # Нахождение серии (поиск зависимых слов от главного)
    tags = find_series(line, tokens, tags, method)

    return {
        "tokens": tokens,
        "tags": tags
    }

# Обработка множества строк
def mark_lines(lines, method="spacy"):
    data = []

    # Для spaCy используем pipe
    if method == "spacy":
        docs = list(spacy_pipeline.pipe(lines))
    # Для UDPipe передаем текстовые строки
    elif method == "udpipe":
        docs = lines  
    else:
        raise ValueError(f"Неизвестный метод: {method}")

    # Многопоточная обработка
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for doc in docs:
            future = executor.submit(process_line, doc, method)
            futures.append(future)

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            data.append(future.result())
            print('step', i)
            
    return data

if __name__ == "__main__": 

    with open('full_pipeline\\data\\corpus_modified_3.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]  # Убирает \n и другие пробельные символы в начале и конце строки

    # lines = [
    #      "Прекращение лечения не сопровождается развитием синдрома «отмены».",
    #      "Периндоприл оказывает сосудорасширяющее действие, способствует восстановлению эластичности крупных артерий и структуры сосудистой стенки мелких артерий, а также уменьшает гипертрофию левого желудочка. ",
    #      "Одновременное применение тиазидных диуретиков усиливает выраженность антигипертензивного эффекта.",
    #      "Кроме этого, комбинирование ингибитора АПФ и тиазидного диуретика также приводит к снижению риска развития гипокалиемии на фоне снижение ОПСС, повышение сердечного выброса и увеличение сердечного индекса.",
    #      "Исследование периндоприла по сравнению с плацебо показало, приема диуретиков.",
    #      "Сердечная недостаточность Периндоприл нормализует работу сердца, снижая преднагрузку и постнагрузку.",
    #      "У пациентов с хронической сердечной недостаточностью (ХСН), получавших периндоприл, было выявлено снижение давления наполнения в левом и правом желудочках сердца, снижение ОПСС, повышение сердечного выброса и увеличение сердечного индекса.",
    #      "Исследование периндоприла по сравнению с плацебо показало, что изменение АД после деменции, связанной с инсультом, а также серьезных ухудшений когнитивных функций.",
    #      "Данные терапевтические преимущества наблюдаются как у пациентов с артериальной первого приема периндоприла у пациентов с ХСН (II – III функциональный класс по классификации NYHA) статистически гипертензией, так и при нормальном АД, независимо от возраста, пола, наличия или отсутствия сахарного диабета и типа инсульта.",
    # ]

    # data = mark_lines(lines)

    start_time = time.time()
    with open("full_pipeline\\data\\mark_sent_4.json", 'w', encoding='utf-8') as file_res:
        json.dump(mark_lines(lines, method="spacy"), file_res, ensure_ascii=False, indent=4)
    end_time = time.time()
    print("Время работы разметки с помощью библиотеки spacy:", end_time-start_time, end='\n\n')

    # start_time = time.time()
    # with open("full_pipeline\\data\\example_udpipe.json", 'w', encoding='utf-8') as file_res:
    #     json.dump(mark_lines(lines, method="udpipe"), file_res, ensure_ascii=False, indent=4)
    # end_time = time.time()
    # print("Время работы разметки с помощью библиотеки udpipe:", end_time-start_time, end='\n\n')