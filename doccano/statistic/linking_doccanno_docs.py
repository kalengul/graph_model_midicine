import json


def process_jsonl_file(filename, id_start_list):
    """
    Читает JSONL-файл построчно, разбивает данные на списки на основе id_start_list.
    
    :param filename: Имя файла JSONL.
    :param id_start_list: Список индексов строк (начиная с 1), указывающих на начало нового списка.
    :return: Список списков словарей.
    """
    id_start_list = iter(sorted(id_start_list))     # Сортировка id_start_list
    id_start = next(id_start_list, None)            # Первый элемент
    result, current_list = [], []

    with open(filename, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file, 1):              # Нумерация строк
            line_dict = json.loads(line.strip())

            # Проверяем, является ли текущая строка началом нового списка
            if i == id_start:
                if current_list:                        # Если не пуст, добавить
                    result.append(current_list)
                current_list = []                       # Новый список
                id_start = next(id_start_list, None)    # Следующий id_start

            current_list.append(line_dict)

    # Добавляем последний список, если он не пуст
    if current_list:
        result.append(current_list)

    return result

def adding_in_1(lists):
    list_dicts = []
    # Цикл по каждому списку
    for i, lst in enumerate(lists, 1):
        # Цикл по строкам внутри списка
        counter_char = 0
        general_dict = {
            "id": i,
            "text": "",
            "entities": [],
            "relations":[]
        }
        for j, item in enumerate(lst, 1):
            item_text = item["text"]
            cur_offset = 10000 * j

            general_dict["text"] += item_text
                
            # Конвертация сущностей с сохранением уникальности id
            for ent in item["entities"]:
                ent["id"] += cur_offset
                ent["start_offset"] = counter_char + ent["start_offset"]
                ent["end_offset"]   = counter_char + ent["end_offset"]
                general_dict["entities"].append(ent)
            
            # Конвертация связей с сохранением уникальности id
            for rel in item["relations"]:
                rel["id"]       += cur_offset
                rel["from_id"]  += cur_offset
                rel["to_id"]    += cur_offset
                general_dict["relations"].append(rel)

            counter_char += len(item_text.replace("\\/", "/"))

        list_dicts.append(general_dict)
            
    return list_dicts


# Пример использования
filename = 'data\\data_4.jsonl'  
file_path_res = 'data\\data_adding.jsonl' 
id_start_list = [8,15,22,27,34,41,47,
                 59,65,72,79,86,92,99,106,
                 113,120,124,127,133,137,140,
                 144,145,146,147,148,149]
lists = process_jsonl_file(filename, id_start_list)

# Вывод результата
file_path_add_drug = 'data\\drug_data'
for i, lst in enumerate(lists, 1):
    print(f"Список {i}:")

    with open(f"{file_path_add_drug}\\drug{i}.jsonl", 'w', encoding='utf-8') as file_res:
        for item in lst:
            json.dump(item, file_res, ensure_ascii=False)
            file_res.write("\n")


result = adding_in_1(lists)
# Сохранение результата
with open(file_path_res, 'w', encoding='utf-8') as file_res:
    for line in result:
        json.dump(line, file_res, ensure_ascii=False)
        file_res.write("\n")

# # Вывод результата
# for i, lst in enumerate(lists, 1):
#     print(f"Список {i}:")
#     for item in lst:
#         print(item["id"])
