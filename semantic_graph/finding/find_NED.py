import json
import re

import os

import pymorphy3
morph = pymorphy3.MorphAnalyzer()


# Деление текста на предложения (1 предложение == 1 строчка)
# Принимает только строку (не список)
def find_sentences_around_period(text):
    
    abbreviations_entr = {
    "ммрт.ст.", "рт.ст.", "ст.", "т.д.", "т.е.", "т.п.", "т.н.", "др.", "т.к.", #"нед.",
    }

    abbreviations_no_entr = {"т.ч."}

    # Регулярное выражение для поиска сокращения перед точкой и слова после точки
    pattern = r'(\b\w+\.?\w*)\.\s+(\w+)'

    # Регулярное выражение для поиска одного или нескольких пробелов перед точками после круглой скобки
    text = re.sub(r'\)\.\s+', '). \n', text)
    # Регулярное выражение для замены "%. " на "%. \n"
    text = re.sub(r'%\.\s', '%.\n', text)

    # Находим все совпадения по регулярному выражению
    matches = list(re.finditer(pattern, text))  # Преобразуем в список для безопасного изменения текста

    if not matches:
        return text  # Если нет совпадений, возвращаем оригинальный текст
    
    modified_text = text  # Копия текста для внесения изменений

    for match in matches:
        sentence_before, sentence_after = match.groups()
        # Убираем пробелы по краям и восстанавливаем точку
        sentence_before = sentence_before.strip() + '.'
        sentence_after = sentence_after.strip()
        first_word_after = sentence_after.split()[0]

        # print("sentence_before:", sentence_before)
        # print("sentence_after:", sentence_after)
        # print('\n')

        # Проверка, начинается ли слово после точки с заглавной буквы
        if first_word_after[0].isupper():
            
            # "Р2Д2", "ЖКТ"...
            if len(first_word_after) > 1 and (first_word_after[1].isupper() or first_word_after[1].isdigit()):
                
                # "и т.д. ЖКТ действует на..."
                if sentence_before in abbreviations_entr:
                    # Запрашиваем у пользователя, ставить ли \n
                    response = input(f"Предложение после '{sentence_before} {first_word_after}'. Хотите поставить '\\n'? (да/нет): ").strip().lower()
                    if response in ('да', 'д', 'y', 'yes'):
                        modified_text = modified_text.replace(f"{sentence_before} {sentence_after}", f"{sentence_before} \n{sentence_after}", 1)
                
                # "в т.ч. ЖКТ действует на..."
                elif sentence_before in abbreviations_no_entr:
                    pass
                
                # "...конец предложения. ЖКТ дейсвует на..."
                else:
                    modified_text = modified_text.replace(f"{sentence_before} {sentence_after}", f"{sentence_before} \n{sentence_after}", 1)
            
            # "...конец предложения. Начало предложения..."
            else:
                modified_text = modified_text.replace(f"{sentence_before} {sentence_after}", f"{sentence_before} \n{sentence_after}", 1)

        # "...и др. симптомы..."
        else:
            pass  # Ничего не делаем

    # Возвращаем измененный текст
    return modified_text

def read_corpus(name, parse_sent = True):
    with open(f"one_corpus\\{name}.txt", 'r', encoding='utf-8') as file:
        text = file.read()

    if parse_sent:
        # Удалить "ненужную" информацию
        text = delete_fragments(text)

        # Разделить построчно
        text = find_sentences_around_period(text)

    return text

# Открытие json файла и извлечение текста
def read_json_drug(drug_name, chapter = None):
    with open(f'json_drug_without_chapter\\{drug_name}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        name = data['Название']
        
    if chapter:
        return data[chapter]
    else:
        return data

# Запись корпуса
def write_corpus(name, text):
    with open(f"one_corpus\\{name}.txt", 'w', encoding='utf-8') as file:

        # Если каждое предложение -- элемент списка
        if isinstance(text, list):
            for sentence in text:
                file.write(sentence + '\n')
        # Иначе
        else:
            file.write(text)

# Открытие словаря с последующей сортировкой количеству слов
def open_dictionary(name):

    # Подсчёт количества слов
    def count_words(string):
        return len(string.split())

    # Чтение JSON файла
    with open(f'json_files\\{name}.json', 'r', encoding='utf-8-sig') as file:
        data = json.load(file)

    # Сортировка списков по количеству слов в элементах
    def sort_lists(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    # Проверяем, что элементы списка являются строками
                    if all(isinstance(item, str) for item in value):
                        data[key] = sorted(value, key=lambda x: count_words(x), reverse=True)
                elif isinstance(value, (dict, list)):
                    sort_lists(value)
        # Если список
        elif isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    sort_lists(item)

    sort_lists(data)

    return data

# Удаление фрагментов (не несёт информацию)
def delete_fragments(text):

    text = re.sub(r'\(.*?\)', '', text)                                         # Удаление круглых скобок и их содержимого

    # text = re.sub(r' \(см\..*?\)', '', text)                                    # "(см. ... )"
    # text = re.sub(r' \(исследование.*?\)', '', text)                            # "(исследование ... )"
    text = re.sub(r'^Таблица.*\d+$', '', text, flags=re.MULTILINE)              # "Таблица n"
    text = re.sub(r'^RxList\.com.*$', '', text, flags=re.MULTILINE)             # "RxList.com ..."
    text = re.sub(r',? показаны в таблице \d+', '', text)                       # ", показаны в таблице n"
    text = re.sub(r'представлен(?:а|о|ы)? в таблице \d+', '', text)             # "представлен(а)(о)(ы) в таблице n"
    text = re.sub(r'приведен(?:а|о|ы)? в таблице \d+', '', text)             # "представлен(а)(о)(ы) в таблице n"
    # text = re.sub(r'\(таблица \d+\)', '', text)                                 # "(таблица n)"

    # # text = re.sub(r'\(от \d+ до \d+ лет\)', '', text)                         # "(от n до m лет)"
    # text = re.sub(r'\(\s*[^)]*?\s+лет\)', '', text)                             # ( ... лет)"
    # text = re.sub(r'\(\s*[^)]*?\s+мес\)', '', text)                             # ( ... мес)"
    # text = re.sub(r'\(\s*[^)]*?\s+нед\)', '', text)                             # ( ... нед)"
    # text = re.sub(r'\(\s*[^)]*?\s+сут\)', '', text)                             # ( ... сут)"

    # text = re.sub(r'\(\d+(?:,\d+)? или \d+(?:,\d+)? мг/сут\)', '', text)        # "(n или m мг/сут)"
    # text = re.sub(r'\(\d+ мг/кг/сут\)', '', text)                               # "(n мг/кг/сут)"

    # text = re.sub(r'\(\d+\)', '', text)                                          # (n)"

    # text = re.sub(r'\(около \d+%\)', '', text)                                  # "(около <число>%)"
    # text = re.sub(r' \(\d+(?:,\d+)?%\)', '', text)                              # "(n%)"
    # text = re.sub(r'\(\d+(?:,\d+)?–\d+(?:,\d+)?%\)', '', text)                  # "(n-m%)"

    text = re.sub(r'Результаты представлены в таблице \d+.', '', text)          # "Результаты представлены в таблице n"

    # text = re.sub(r'\(например, [^)]*?\)', '', text)                            # "(например, ... )" ???


    # Удалить пробелы в случаях " . ", " , ", " :", " ;"
    text = re.sub(r' +\,', ',', text)
    text = re.sub(r' +\.', '.', text)
    text = re.sub(r' +\:', ':', text)
    text = re.sub(r' +\;', ';', text)
    text = re.sub(r'\,\.', '.', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\n+', '\n', text)
    return text
    
# Замена сокращений (не аббревиатуры) на полные выражения (т.е. -> то есть)
def replace_reduses(text, dictionary):
    # Замена сокращений на целые слова
    redudeses_dict = dictionary["Reduses"]
    for key, value in redudeses_dict.items():
        if isinstance(value, list):
            for synonym in value:
                # Экранирование специальных символов
                pattern = re.escape(synonym)
                text = re.sub(pattern, key, text)
        elif isinstance(value, str):
            # Экранирование специальных символов
            pattern = re.escape(value)
            text = re.sub(pattern, key, text)

    return text

# Замена сокращений (не аббревиатуры) на полные выражения (т.е. -> то есть)
def replace_test(text, dictionary):
    # Замена сокращений на целые слова
    redudeses_dict = dictionary["Test"]
    for key, value in redudeses_dict.items():
        if isinstance(value, list):
            for synonym in value:
                # Экранирование специальных символов
                pattern = re.escape(synonym)
                text = re.sub(pattern, key, text)
        elif isinstance(value, str):
            # Экранирование специальных символов
            pattern = re.escape(value)
            text = re.sub(pattern, key, text)

    return text


def lemmatize_word(word):
    return morph.parse(word.lower())[0].normal_form

def lemmatize_phrases(phrases):
    # Удаляем небуквенные символы и лемматизируем фразы
    return [
        ' '.join(lemmatize_word(word) for word in re.sub(r'[^\w\s]', '', phrase).lower().split())
        for phrase in phrases
    ]

counter = 0
def mark_words_in_line(line, lemmatized_phrases):
    # Разделяем строку по разделителям ",", ";", ":"
    chunks = re.split(r'[,:;]', line)
    marked_chunks = []
        
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        
        # Лемматизируем слова в текущем кусочке
        words = [(m.group(0), m.start(), m.end()) for m in re.finditer(r'\b\w+\b', chunk)]
        lemmatized_words = [lemmatize_word(word) for word, _, _ in words]
        lemmatized_chunk = ' '.join(lemmatized_words)
        
        # Создаем шаблон регулярного выражения для поиска фраз
        pattern = r'\b(' + '|'.join(map(re.escape, lemmatized_phrases)) + r')\b'
        marked_chunk_parts = []
        last_end = 0
        
        for match in re.finditer(pattern, lemmatized_chunk):
            start, end = match.span()
            matched_phrase = match.group(0)
            
            start_idx = lemmatized_chunk[:start].count(' ')
            end_idx = start_idx + matched_phrase.count(' ') + 1
            
            original_start_idx = words[start_idx][1]
            original_end_idx = words[end_idx - 1][2]
            
            original_phrase = chunk[original_start_idx:original_end_idx]
            
            marked_chunk_parts.append(chunk[last_end:original_start_idx])
            marked_chunk_parts.append(f'[{original_phrase}]')
            
            last_end = original_end_idx
        
        marked_chunk_parts.append(chunk[last_end:])
        marked_chunks.append(''.join(marked_chunk_parts))
    
    global counter
    counter += 1
    print(counter)

    return ', '.join(marked_chunks)

def mark_words_in_text(text, phrases):
    # Лемматизируем фразы
    lemmatized_phrases = lemmatize_phrases(phrases)
    
    # Разбиваем текст на строки и обрабатываем каждую строку отдельно
    return '\n'.join(mark_words_in_line(line, lemmatized_phrases) for line in text.split('\n'))


text = """При почечной недостаточности необходимо проведение гемодиализа или перитонеального диализа.
Ингибирует ксантиноксидазу, нарушает превращение гипоксантина в ксантин и ксантина — в мочевую кислоту; ограничивает таким образом синтез мочевой кислоты. 
Понижает содержание уратов в сыворотке крови и предотвращает отложение их в тканях, в т.ч. почечной. Уменьшает выведение с мочой мочевой кислоты и повышает — более легкорастворимых гипоксантина и ксантина.
Почти полностью абсорбируется из ЖКТ. 
В печени под влиянием ксантиноксидазы превращается в аллоксантин, который также препятствует образованию мочевой кислоты. 
Cmax аллопуринола достигается через 1,5 ч, аллоксантина — через 4,5 ч после однократного приема. 
T1/2 аллопуринола составляет 1–2 ч, аллоксантина — около 15 ч. 
Около 20% дозы выводится через кишечник; остальная часть аллопуринола и его метаболитов — почками.
Гиперчувствительность, печеночная недостаточность, хроническая почечная недостаточность, первичный гемохроматоз, бессимптомная гиперурикемия, острый приступ подагры, беременность, грудное вскармливание.
Почечная недостаточность, хроническая сердечная недостаточность, сахарный диабет, артериальная гипертензия, детский возраст.
Категория действия на плод по FDA — C.
Со стороны органов ЖКТ: тошнота, рвота, боль в животе, диарея, стоматит, гипербилирубинемия, холестатическая желтуха, повышение активности печеночных трансаминаз и ЩФ; редко — гепатонекроз, гепатомегалия, гранулематозный гепатит.
Со стороны сердечно-сосудистой системы и крови: перикардит, повышение АД, брадикардия, васкулит, агранулоцитоз, анемия, апластическая анемия, тромбоцитопения, эозинофилия, лейкоцитоз, лейкопения.
Со стороны опорно-двигательного аппарата: миопатия, миалгия, артралгия.
Со стороны нервной системы и органов чувств: головная боль, периферическая невропатия, неврит, парестезии, парез, депрессия, сонливость, извращение вкуса, потеря вкусовых ощущений, нарушение зрения, катаракта, конъюнктивит, амблиопия.
Со стороны мочеполовой системы: острая почечная недостаточность, интерстициальный нефрит, повышение концентрации мочевины, периферические отеки, гематурия, протеинурия, снижение потенции, бесплодие, гинекомастия.
Аллергические реакции: кожная сыпь, кожный зуд, крапивница, многоформная экссудативная эритема, токсический эпидермальный некролиз, пурпура, буллезный дерматит, экзематозный дерматит, эксфолиативный дерматит; редко — бронхоспазм.
Прочие: фурункулез, алопеция, сахарный диабет, обезвоживание, носовое кровотечение, некротическая ангина, лимфаденопатия, гипертермия, гиперлипидемия.
Повышает концентрацию в крови и токсичность азатиоприна, меркаптопурина, метотрексата, ксантинов, гипогликемический эффект хлорпропамида, противосвертывающий — непрямых антикоагулянтов. 
Пиразинамид, салицилаты, урикозурические средства, тиазидные диуретики, фуросемид, этакриновая кислота ослабляют гипоурикемическое влияние. 
На фоне амоксициллина, ампициллина, бакампициллина возрастает вероятность появления кожной сыпи.
Симптомы: тошнота, рвота, диарея, головокружение, олигурия.
Лечение: форсированный диурез, гемо- и перитонеальный диализ.
Связываясь с бензодиазепиновыми и ГАМКергическими рецепторами, вызывает торможение лимбической системы, таламуса, гипоталамуса, полисинаптических спинальных рефлексов.
После приема внутрь быстро абсорбируется из ЖКТ. 
Cmax достигается через 1–2 ч. 
Связывание с белками плазмы составляет 80%.
Проходит через ГЭБ и плацентарный барьер, проникает в грудное молоко. 
Метаболизируется в печени. 
T1/2 — 16 ч. 
Выводится преимущественно почками. 
Повторное назначение с интервалом менее 8–12 ч может приводить к кумуляции.
Гиперчувствительность, выраженная дыхательная недостаточность, глаукома, острые заболевания печени и почек, миастения, беременность, кормление грудью, возраст до 18 лет.
Открытоугольная глаукома, апноэ во время сна, хроническая почечная и/или печеночная недостаточность, алкогольное поражение печени.
Категория действия на плод по FDA — D.
Сонливость, усталость, головокружение, шаткость походки, замедление психических и двигательных реакций, снижение концентрации внимания, тошнота, запор, дисменорея, снижение либидо, кожный зуд, парадоксальные реакции, привыкание, лекарственная зависимость, синдром отмены.
Усиливает действие алкоголя, нейролептиков и снотворных средств, наркотических анальгетиков, центральных миорелаксантов. 
Увеличивает концентрацию имипрамина в сыворотке.
Симптомы: угнетение ЦНС различной степени выраженности — сонливость, спутанность сознания; в более тяжелых случаях — атаксия, снижение рефлексов, гипотензия, кома.
Лечение: индукция рвоты, промывание желудка, симптоматическая терапия, мониторинг жизненно важных функций. 
При выраженной гипотензии — введение норэпинефрина. 
Специфический антидот — антагонист бензодиазепиновых рецепторов флумазенил.
Алпростадил обладает широким спектром фармакологического действия. 
Среди наиболее значимых его эффектов — вазодилатация, подавление агрегации тромбоцитов, стимулирующее влияние на гладкую мускулатуру кишечника, матки и других гладкомышечных органов. 
Улучшает микроциркуляцию, повышает периферический кровоток, оказывает вазопротективное действие. 
При системном введении вызывает расслабление гладкомышечных волокон сосудистой стенки, оказывает сосудорасширяющее действие, уменьшает ОПСС, понижает АД. 
При этом отмечается рефлекторное увеличение сердечного выброса и ЧСС. 
Способствует повышению эластичности эритроцитов, уменьшает агрегацию тромбоцитов и активность нейтрофилов, повышает фибринолитическую активность крови.
Гладкомышечные клетки артериального протока обладают высокой чувствительностью к действию алпростадила, что позволяет применять его у новорожденных детей с врожденными ductus-зависимыми пороками сердца, в т.ч. при митральной атрезии, атрезии легочной артерии, трехстворчатого клапана, тетраде Фалло. 
Алпростадил применяют для паллиативного лечения до проведения хирургической операции. 
Использование алпростадила позволяет поддерживать артериальный проток в открытом состоянии, что улучшает кровообращение и оксигенацию. 
Лечение алпростадилом в этом случае является в основном кратковременной мерой, но иногда может потребоваться длительная терапия.
Действие алпростадила при лечении нарушений эрекции связано с угнетением альфа1-адренергической передачи в тканях полового члена и расслабляющим действием на гладкую мускулатуру пещеристых тел. 
"""

text = read_corpus('corpus_modified_2', parse_sent= False)               # Прочесть корпус

data = open_dictionary('Dictionary')
marked_text = mark_words_in_text(text, data['SideEffects'])

write_corpus('corpus_marked_text', marked_text)         # Записать корпус







    