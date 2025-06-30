import json
import re
import pymorphy3

# Инициализация лемматизатора
morph = pymorphy3.MorphAnalyzer()

def save_excel(final_results, output_file = "categorized_results_prefix.xlsx"):
    import pandas as pd

    # Объединение всех списков из каждого префикса
    prilag_list = []
    glagol_list = []
    substance_list = []
    side_effect_list = []

    for prefix, categories in final_results["PrefixResults"].items():
        prilag_list.extend(categories.get("prilag", []))
        glagol_list.extend(categories.get("glagol", []))
        substance_list.extend(categories.get("substance", []))
        side_effect_list.extend(categories.get("side_effect", []))

    # Создание DataFrame из объединённых списков
    data = {
        "prilag": prilag_list,
        "glagol": glagol_list,
        "substance": substance_list,
        "side_effect": side_effect_list
    }

    # Создание DataFrame
    df = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in data.items()]))

    # Запись DataFrame в Excel файл
    df.to_excel(output_file, index=False)

    print(f"Excel файл '{output_file}' успешно создан.")

def categorize_words(pref_res_file, prefixes_file):

    # Чтение текстового файла
    with open("one_corpus\\corpus_modified_2.txt", 'r', encoding='utf-8') as file:
        text_lower = file.read()

    # Добавить элементы списков из словаря
    def add_side_effects(text_lower):
        # Загрузка JSON словаря с побочками
        with open('json_files\\SideEffects_n_Word.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Объединение всех слов из SideEffects_1_Word и SideEffects_2_Word
        side_effects_1_word = data.get('SideEffects_1_Word', [])
        side_effects_2_word = data.get('SideEffects_2_Word', [])

        # Объединение текста из файла и слов из списков в одну строку
        text_lower = text_lower + " " + " ".join(side_effects_1_word) + " " + " ".join(side_effects_2_word)

        return text_lower
    
    # Добавить слова из МКБ-10
    def add_mkb_10_word(text_lower):
        # Чтение JSON-файла и извлечение слов из него
        with open('word_frequencies.json', 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        words = data['Общие частотности'].keys()
        text_lower = text_lower + " " + " ".join(words)

        return text_lower


    text_lower = add_side_effects(text_lower)
    text_lower = add_mkb_10_word(text_lower)
    text_lower = text_lower.lower()


    # Чтение, сортировка, запись префиксов обратно в отсортированном виде
    def read_prefixes_file(prefixes_file):
        # Чтение JSON файла с префиксами
        with open(f'json_files\\{prefixes_file}.json', 'r', encoding='utf-8-sig') as file:
            prefixes_data = json.load(file)

        prefixes_list = prefixes_data.get('Prefix', [])

        # Сортировка словаря по префиксам
        sorted_prefixes_list  =  sorted(prefixes_list)

        sorted_prefixes_dict = {'Prefix': sorted_prefixes_list}

        # Чтение JSON файла с результатами префиксов
        with open(f'json_files\\{prefixes_file}.json', 'w', encoding='utf-8-sig') as file:
            json.dump(sorted_prefixes_dict, file, ensure_ascii=False, indent=4)

        return prefixes_list
    
    # Проверка на "лишние" префиксы, которые могли удалить
    def read_prefixes_result(pref_res_file, prefixes_list):
        # Чтение JSON файла с результатами префиксов
        with open(f'json_files\\{pref_res_file}.json', 'r', encoding='utf-8-sig') as file:
            data = json.load(file)

        prefix_results = data.get('PrefixResults', {})

        # Оставить только те префиксы, которые есть в prefixes_list
        filtered_prefix_results = {prefix: categories for prefix, categories in prefix_results.items() if prefix in prefixes_list}

        return filtered_prefix_results

    # Список ключей из файла prefixes_sideEffect
    prefixes_list = read_prefixes_file(prefixes_file)

    # Список ключей из файла Result, но только те, которые есть в prefixes_list
    prefix_results = read_prefixes_result(pref_res_file, prefixes_list)

    # Добавление отсутствующих префиксов в результаты
    for prefix in prefixes_list:
        if prefix not in prefix_results:
            prefix_results[prefix] = {
                "exeption": [],   # Список исключений
                "prilag": [],     # Прилагательные
                "glagol": [],     # Глаголы
                "substance": [],  # Субстанции, заканчивающиеся на "ид", "ол", "ин", "он", "ан", "ат", "ен"
                "noun_ie": [],    # Существительные, заканчивающиеся на "ие"
                "side_effect": [] # Остальные слова
            }
            print("Добавлена новая приставка:", prefix)

    # Инициализация словаря для хранения результатов
    categorized_results = {}

    for prefix, categories in prefix_results.items():
        # Инициализация категорий
        exeption_list = categories.get("exeption", [])
        prilag_list = []
        glagol_list = []
        substance_list = []
        noun_ie_list = []
        side_effect_list = [] 

        categorized_results[prefix] = {
            "exeption": exeption_list,   # Список исключений, если существует
            "prilag": prilag_list,       # Прилагательные
            "glagol": glagol_list,       # Глаголы
            "substance": substance_list, # Субстанции, заканчивающиеся на "ид", "ол", "ин", "он", "ан", "ат", "ен"
            "noun_ie": noun_ie_list,    # Существительные, заканчивающиеся на "ие"
            "side_effect": side_effect_list  # Остальные слова
        }

        prefix_lower = prefix.lower()
        # Используем регулярное выражение для поиска слов, начинающихся с префикса
        pattern = r'\b' + re.escape(prefix_lower) + r'\w*\b'
        matches = re.findall(pattern, text_lower)
        # Лемматизация найденных слов
        lemmas = [morph.parse(word)[0].normal_form for word in matches]
        # Удаление повторений и сортировка результатов
        unique_lemmas = sorted(set(lemmas))

        words = unique_lemmas
        for word in words:

            # Проверяем, начинается ли слово с любого символа из exeption_list
            if any(word.startswith(char) for char in exeption_list) or word == prefix_lower or len(word) <= len(prefix_lower):
                continue  # Пропускаем слово, если оно начинается с символа из exeption_list

            # Проверяем, есть ли на конце слова цифра, и убираем её
            word = re.sub(r'\d$', '', word)

            parsed_word = morph.parse(word)[0]
            normal_form = parsed_word.normal_form
            tag = parsed_word.tag

            # Пропускаем слово, если оно совпадает с префиксом
            if word == prefix_lower:
                continue  
            elif 'ADJF' in tag or 'ADJS' in tag:
                prilag_list.append(normal_form)
            elif 'VERB' in tag or 'INFN' in tag:
                glagol_list.append(normal_form)
            elif normal_form.endswith(("ид", "ол", "ин", "он", "ан", "ат", "ен", "ик", "ант", "ил")):
                substance_list.append(normal_form)
            elif normal_form.endswith("ие"):
                noun_ie_list.append(normal_form)
            else:
                side_effect_list.append(normal_form)

        # Удаление повторений и сортировка результатов
        for key in categorized_results[prefix]:
            categorized_results[prefix][key] = sorted(set(categorized_results[prefix][key]))

    # Сортировка словаря по префиксам
    sorted_categorized_results  =  dict(sorted(categorized_results.items()))

    # Создание итогового словаря
    final_results = {"PrefixResults": sorted_categorized_results }

    save_excel(final_results)

    # Сохранение словаря в JSON-файл
    # output_file_path = 'PrefixResults.json'
    with open(f'json_files\\{pref_res_file}.json', 'w', encoding='utf-8') as file:
        json.dump(final_results, file, ensure_ascii=False, indent=4)

    print(f"Данные сохранены в json_files\\{pref_res_file}")

# Пример использования
categorize_words('PrefixResults', 'prefixes_sideeffect')  # замените 'PrefixResults' и 'prefixes_sideeffect' на имена ваших JSON-файлов без расширения
