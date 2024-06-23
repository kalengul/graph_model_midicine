import sys
sys.path.append('./Work')

from bs4 import BeautifulSoup       # Парсер html
import re                           # Регулярки

drug = 'aliskiren'
file_name = f'{drug}_age_sex_html.txt'
dir_name_dest = 'age_sex'

class drug_row():
    def __init__(self, argument, count, percentage):
        self.argument = argument
        self.count = count
        self.percentage = percentage

def open_age_sex_html(file_name):
    # drug = 'temsirolimus'

    drug_sex_list = []
    drug_age_list = []
    drug_name = file_name.split('_age_sex_html.txt')[0]

    # Открытие файла с разметкой страницы
    try:
        with open(f'drugs_age_sex_html\\{file_name}', 'r', encoding='utf-8') as file:
            # Если файл открыт успешно, можно выполнять операции с ним здесь
            print(f"Файл успешно открыт {file_name}")

            drug_sex_list = parse_age_sex(file.readline(), 0)
            drug_age_list = parse_age_sex(file.readline(), 1)
    except FileNotFoundError:
        print("Файл не найден")
        return -1
    except IOError:
        print("Ошибка ввода-вывода при открытии файла")
        return -2
    
    return drug_sex_list, drug_age_list

    
def write_age_sex(drug_name, list_sex, list_age):
    # Открытие файла с разметкой страницы
    try:
        with open(f'age_sex\\{drug_name}.txt', 'w', encoding='utf-8') as file:
            # Если файл открыт успешно, можно выполнять операции с ним здесь
            print(f"Файл успешно открыт {drug_name}")
            
            file.write("***\n")
            file.write("Пол\n")
            for obj in list_sex:
                file.write(f'{obj.argument} / {obj.count} / {obj.percentage}\n')

            file.write("***\n")
            file.write("Возраст\n")
            for obj in list_age:
                file.write(f'{obj.argument} / {obj.count} / {obj.percentage}\n')

            return 0
    except FileNotFoundError:
        print("Файл не найден")
        return -1
    except IOError:
        print("Ошибка ввода-вывода при открытии файла")
        return -2
    
def parse_age_sex(html_content, i):

    # Создание объекта BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    data_dict  = {}

    # if i == 0:
    #     print("Пол: ")
    # if i == 1:
    #     print("Возраст: ")

    # Нахождение всех тегов <li> их содержимое
    for tr_tag in soup.find_all('tr'):

        td_tags_in_tr = tr_tag.find_all('td')

        # Данные таблицы
        if len(td_tags_in_tr) > 0:

            row = td_tags_in_tr[0].get_text()

            # Преобразование
            count = td_tags_in_tr[1].get_text()
            count = re.sub(r'[^\x00-\x7F]+', '', count)
            count = int(count)

            percentage = td_tags_in_tr[2].get_text()

            data_dict[row] = count

            # list.append(drug_row(row, count, percentage))

            # # Пол
            # if i == 0: 
            #     row = td_tags_in_tr[0].get_text()
            #     count = td_tags_in_tr[1].get_text()
            #     percentage = td_tags_in_tr[2].get_text()

            #     # print("sex:", row, "count:", count, "percentage:", percentage)

            # # Возраст
            # if i == 1:
            #     row = td_tags_in_tr[0].get_text()
            #     count = td_tags_in_tr[1].get_text()
            #     percentage = td_tags_in_tr[2].get_text()

                # print("age_group:", row, "count:", count, "percentage:", percentage)

            # list.append(drug_row(row, count, percentage))

    return data_dict

drug_sex_list, drug_age_list = open_age_sex_html(file_name)
for возраст, количество in drug_age_list.items():
    print(f"Возраст: {возраст}, Количество: {количество}")

for возраст, количество in drug_sex_list.items():
    print(f"Пол: {возраст}, Количество: {количество}")
# write_age_sex(drug_name, drug_sex_list, drug_age_list)