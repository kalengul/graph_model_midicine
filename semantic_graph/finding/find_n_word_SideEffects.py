import json

def count_words(string):
    return len(string.split())

def find_n_word(file_path):
    # Чтение JSON файла
    with open(f'json_files\\{file_path}.json', 'r', encoding='utf-8-sig') as file:
        data = json.load(file)
        
    side_effects = data['SideEffects']

    # Проверяет, состоит ли элемент из n слов
    def is_n_word(element, count):
        return isinstance(element, str) and len(element.split()) == count

    # Фильтрует элементы, оставляя только те, которые состоят из одного слова
    def filter_n_word_elements(input_list, count):
        return [element for element in input_list if is_n_word(element, count)]

    n_word_side_effcets_list = {}
    for i in range(1, 13):
        # Создание словаря с ключом
        n_word_side_effcets_list[f"SideEffects_{i}_Word"] = filter_n_word_elements(side_effects, i)
        n_word_side_effcets_list[f"SideEffects_{i}_Word"] = sorted(n_word_side_effcets_list[f"SideEffects_{i}_Word"])


    file_path_output = f'SideEffects_n_Word'
    with open(f'json_files\\{file_path_output}.json', 'w', encoding='utf-8') as file:
        json.dump(n_word_side_effcets_list, file, ensure_ascii=False, indent=4)


# Пример использования функции
file_path = 'Dictionary'
find_n_word(file_path)



# def sort_lists_in_json(file_path):
#     # Чтение JSON файла
#     with open(f'{file_path}.json', 'r', encoding='utf-8-sig') as file:
#         data = json.load(file)
    
#     # Сортировка списков по количеству слов в элементах
#     def sort_lists(data):
#         if isinstance(data, dict):
#             for key, value in data.items():
#                 if isinstance(value, list):
#                     # Проверяем, что элементы списка являются строками
#                     if all(isinstance(item, str) for item in value):
#                         data[key] = sorted(value, key=lambda x: count_words(x), reverse=True)
#                 elif isinstance(value, (dict, list)):
#                     sort_lists(value)
#         # Если список
#         elif isinstance(data, list):
#             for index, item in enumerate(data):
#                 if isinstance(item, (dict, list)):
#                     sort_lists(item)

#     sort_lists(data)
   
    
#     # Запись отсортированных данных обратно в JSON файл
#     with open(f'{file_path}_sorted.json', 'w', encoding='utf-8') as file:
#         json.dump(data, file, ensure_ascii=False, indent=4)


# sort_lists_in_json(file_path)