import sys
sys.path.append('./Work')

from bs4 import BeautifulSoup       # Парсер html
import re                           # Регулярки

from googletrans import Translator  # Переводчик
translator = Translator()

from parse_age_sex_html import open_age_sex_html

import time
import random

class drug:
    def __init__(self, file_name):

        # # Извлечение названия
        drug_name = file_name.split('_html.txt')[0]

        # Поиск количества обращений в файле "drug_list.txt"
        with open('drug_list.txt', 'r', encoding='utf-8') as file:
            for line in file:
                if drug_name in line:
                    parts = line.strip().split(',')
                    try:
                        name_ru = parts[0].strip()
                        number = int(parts[1].strip())
                        name_en = parts[2].strip()
                    except (IndexError, ValueError):
                        print("Неверный формат числа обращений.")

        self.file_name = file_name
        self.name_ru = name_ru
        self.name_en = name_en
        self.number = number
        self.drug_side_effect_list = parse_side_effect_drug(file_name)
        self.drug_sex_list, self.drug_age_list = open_age_sex_html(f'{drug_name}_age_sex_html.txt')

    # Печать побочных явлений
    def print_side_effect(self, index=None):
        # print(f"{self.name_ru}:")
        if index is None:
            for item in self.drug_side_effect_list:
                self.print_item(item)
        else:
            if 0 <= index < len(self.drug_side_effect_list):
                self.print_item(self.drug_side_effect_list[index])
            else:
                print("Неверный индекс.")

    def print_item(self, item):
        print("* ", item.name, item.percents, item.cases)
        for sub_side in item.sub_side_effect:
            print("##\t", sub_side['name'], sub_side['cases'])

    # Количество разных побочек
    def get_len_list(self):
        len = 0
        for item in self.drug_side_effect_list:
            len += len(item)
        return len


class side_effect:
    def __init__(self, text):
        # Преобразование в UTF-8
        utf8_text = text.encode('utf-8')

        # Уборка невидимых символов
        visible_text = re.sub(r'[^\x00-\x7F]+', '', utf8_text.decode('utf-8'))

        # Регулярное выражение для разделения текста на название, проценты, количество случаев и побочные эффекты
        matches = re.search(r'(.+)\s+\((\d+)%,\s*(\d+)\s+ADRs\)', visible_text)

        if matches:
            name = matches.group(1).strip()             # Название
            percent = int(matches.group(2))             # Количество процентов
            cases = int(matches.group(3))               # Количество случаев

        self.name = name
        # self.name = translator.translate(name, src='en', dest='ru').text
        self.percents = percent
        self.cases = cases
        self.sub_side_effect = {}

def parse_sub_side_effect(text):
    # Уборка невидимых символов
    visible_text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    # Применение регулярного выражения для разделения текста на название и количество
    matches = re.search(r'(.+)\s*\((\d+)\)\s*', visible_text)
    # dict = {}
    if matches:
        name = matches.group(1).strip()                     # Название
        quantity = int(matches.group(2))                    # Количество
        # return {"name": name, "cases": quantity}
        # dict[name] = quantity
        return name, quantity
        # time.sleep(0.21)
        # return {"Название": translator.translate(name, src='en', dest='ru').text, "Количество": quantity}
        
    else:
        return {"Ошибка": "Не удалось распарсить текст."}

# def print_side_effect_drug(file_name, drug_side_effect_list, index=None):
#     # Печать имени файла и названия лекарства
#     print("Файл:", file_name)
#     drug_name = file_name.split('_html.txt')[0]
#     print("Название лекарства:", drug_name)

#     # Поиск количества обращений в файле "drug_list.txt"
#     with open('drug_list.txt', 'r', encoding='utf-8') as file:
#         for line in file:
#             if drug_name in line:
#                 parts = line.strip().split(',')
#                 try:
#                     number = int(parts[1].strip())
#                     print("Число обращений:", number)
#                 except (IndexError, ValueError):
#                     print("Неверный формат числа обращений.")

#     # Печать побочных явлений
#     print(f"{drug_name}:")
#     if index is None:
#         for item in drug_side_effect_list:
#             print_item(item)
#     else:
#         if 0 <= index < len(drug_side_effect_list):
#             print_item(drug_side_effect_list[index])
#         else:
#             print("Неверный индекс.")

# def print_item(item):
#     print("* ", item.name, item.percents, item.cases)
#     for sub_side in item.sub_side_effect:
#         print("##\t", sub_side['Название'], sub_side['Количество'])


def parse_side_effect_drug(file_name):
    # drug = 'temsirolimus'

    # Открытие файла с разметкой страницы
    try:
        with open(f'drugs_html\\{file_name}', 'r', encoding='utf-8') as file:
            # Если файл открыт успешно, можно выполнять операции с ним здесь
            print(f"Файл успешно открыт {file_name}")
            html_content = file.read()
    except FileNotFoundError:
        print("Файл не найден")
        return -1
    except IOError:
        print("Ошибка ввода-вывода при открытии файла")
        return -2

    # Создание объекта BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    side_effects_list = []

    # Нахождение всех тегов <li> их содержимое
    for li_tag in soup.find_all('li'):

        # Нахождение тегов <span> в тегах <li>
        span_tags_in_li = li_tag.find_all('span')
        
        # Заболевание
        if(len(span_tags_in_li) > 1):
            reaction = side_effect(li_tag.get_text())
            side_effects_list.append(reaction)
            # print(reaction.name)
        # Симптом
        else:
            name, quantity = parse_sub_side_effect(li_tag.get_text())
            # side_effects_list[-1].sub_side_effect.append(sub_side_effect)
            side_effects_list[-1].sub_side_effect[name] = quantity
            # print("\t", sub_side_effect)

    return side_effects_list