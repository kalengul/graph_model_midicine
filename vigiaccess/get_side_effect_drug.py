import os
from parse_html import parse_side_effect_drug #, print_side_effect_drug


# Извлечение метаданных
drug_list_file_name = 'drug_list.txt'
def get_metadata_drug_report(file_drug_name):
    # Извлечение названия
    drug_name = file_drug_name.split('_html.txt')[0]
 
    # Поиск количества обращений в файле "drug_list.txt"
    with open(drug_list_file_name, 'r', encoding='utf-8') as file:
        for line in file:
            if drug_name in line:
                parts = line.strip().split(',')
                try:
                    name_ru = parts[0].strip()
                    name_en = parts[2].strip()
                    number = int(parts[1].strip())
                except (IndexError, ValueError):
                    print("Неверный формат числа обращений.")

    print("Имя_файла:", file_drug_name,
            "Название_лекарства_ru:", name_ru,
            "Название_лекарства_en:", name_en,
            "Число_обращений:", number)

    return {"file_name": file_drug_name,
            "name_ru": name_ru,
            "name_en": name_en,
            "number": number}


# # Печать списка побочек
# def print_side_effect_drug(file_drug_name, drug_side_effect_list):

#     metadata_drug = get_metadata_drug_report(file_drug_name)

#     print("Файл:", metadata_drug["Имя_файла"])
#     print("Название_лекарства:", metadata_drug["Название_лекарства"])
#     print("Число_обращений:", metadata_drug["Число_обращений"])

#     # Печать побочных явлений
#     print(f"{metadata_drug["Имя_файла"]}:")
#     for item in drug_side_effect_list:
#             print("* ", item.name, item.percents, item.cases)
#             for sub_side in item.sub_side_effect:
#                 print("##\t", sub_side['Название'], sub_side['Количество'])

# Запись в файл
folder_side_effects_en_path = './side_effects_en'
def write_side_effect_drug(file_drug_name, drug_side_effect_list):
    metadata_drug = get_metadata_drug_report(file_drug_name)

    try:
        with open(f'{folder_side_effects_en_path}\\{metadata_drug["Название_лекарства"]}.doc', 'w') as file:
            
            # Печать метаданных в начале файла
            file.write(f"Name_file: {metadata_drug["Имя_файла"]}\n")
            file.write(f"Name_drug: {metadata_drug["Название_лекарства"]}\n")
            file.write(f"Count_report: {metadata_drug["Число_обращений"]}\n")

            # Печать побочных явлений
            for item in drug_side_effect_list:
                    file.write(f"* {item.name} {item.percents} {item.cases}\n")
                    for sub_side in item.sub_side_effect:
                        file.write(f"##\t{sub_side['Название']} {sub_side['Количество']}\n")

    except FileNotFoundError:
        print("Файл не найден")
        return -1


# file_name = "vildagliptin_html.txt"
# drug_side_effect_list = parse_side_effect_drug(file_name)
# write_side_effect_drug(file_name, drug_side_effect_list)

# print_side_effect_drug(file_name, drug_side_effect_list)

# Получаем список файлов в папке
files = os.listdir('./drugs_html')

for file_name in files:
    drug_side_effect_list = parse_side_effect_drug(file_name)
    # Открытие файла с разметкой страницы
    write_side_effect_drug(file_name, drug_side_effect_list)
