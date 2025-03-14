import requests
from bs4 import BeautifulSoup
import json
import re
import time
import csv

from get_side_effects_rlsnet import get_side_effects_rlsnet

def extract_frequency_and_effect(text):
    # Регулярное выражение для разделения текста по первой ":"
    pattern = r'^(.*?):\s*(.*)$'
    match = re.match(pattern, text)
    if match:
        frequency = match.group(1).strip()  # Убираем лишние пробелы
        effect = match.group(2).strip()
        return frequency, effect
    else:
        return None
    
def fetch_page_with_retries(url, max_retries=10, delay=2):
    retries = 0
    success = False

    while retries < max_retries and not success:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверка на успешный статус (например, 200)
            soup = BeautifulSoup(response.content, 'html.parser')
            success = True  # Запрос успешен, выходим из цикла
            # print(f"Successfully fetched: {url}")
            return soup
        except requests.exceptions.RequestException as e:
            retries += 1
            # print(f"Attempt {retries} failed for {url}: {e}")
            time.sleep(delay)  # Задержка перед следующей попыткой

    print(f"Failed to fetch {url} after {max_retries} attempts. Skipping...")
    return None  # Если все попытки не удались, возвращаем None    

def parse_side_effects(drug_name):

    # Создание ссылки
    prefix = 'https://www.drugs.com/sfx/'
    postfix = '-side-effects.html'
    url = f"{prefix}{drug_name.lower()}{postfix}"       
            
    soup = fetch_page_with_retries(url)
    # soup = BeautifulSoup(response.content, 'html.parser')

    if not soup:
        return

    drug_dict = {'drug_name_en':drug_name, }

    # Найти раздел "For Healthcare Professionals"
    professional_section = soup.find('h2', string='For healthcare professionals')
    if not professional_section:
        print('Раздел "For Healthcare Professionals" не найден.')
        return

    # Инициализировать словарь для хранения побочных эффектов
    side_effects = {}

    # Найти все заголовки h3 и соответствующие списки ul после раздела "For healthcare professionals"
    for element in professional_section.find_all_next(['h2', 'h3', 'ul']):
        # Остановить парсинг при встрече следующего тега h2
        if element.name == 'h2' and element != professional_section:
            break
        # Пропустить элемент
        elif element.name == 'h3':
            current_category = element.get_text(strip=True)
            if current_category == 'General adverse events':
                continue
            side_effects[current_category] = {}
        elif element.name == 'ul' and current_category:
            for li in element.find_all('li'):
                # print(li)
                full_text = extract_frequency_and_effect(li.get_text(separator='', strip=True))

                # print(full_text)

                if full_text:
                    frequency, effects = full_text
                    frequency = re.sub(r'\(.*?\)', '', frequency)
                    if frequency not in side_effects[current_category]:  
                        side_effects[current_category][frequency] = []  # Инициализация списка

                    # Обработка effects
                    effects = re.sub(r'\[.*?\]', '', effects)               # Удаляет содержимое в квадратных скобках
                    effects = effects.lower()                               # Понижение регистра
                    effect_list = [effect.strip() for effect in effects.split(",")]

                    side_effects[current_category][frequency].append(effect_list)

    drug_dict['side_effects'] = side_effects
    # # Сохранить результаты в JSON-файл
    # with open(f'data\\side_effects_frequency\\{drug_name}_side_effects.json', 'w', encoding='utf-8') as f:
    #     json.dump(drug_dict, f, ensure_ascii=False, indent=4)

    return drug_dict

    # print('Побочные эффекты успешно сохранены в файл side_effects.json.')



if __name__ == "__main__":
    csv_filename = 'data\\drugs_table.csv'  # Замените на имя вашего CSV-файла

    # Открываем CSV-файл и читаем данные
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')  # Используем `;` как разделитель
        for row in reader:
            result = None
            drug_name_ru = row.get('drug_name_ru', '').strip()
            drug_name_en = row.get('drug_name_en', '').strip()
            drugscom_link = row.get('drugscom_link', '').strip()  
            rlsnet_link = row.get('rlsnet_link', '').strip()

            # print(f"drugscom_link: '{drugscom_link}', rlsnet_link:'{rlsnet_link}'")
            
            # Проверяем, если drug_name пустой или равен 'None', то используем rlsnet_link
            if drugscom_link and drugscom_link != 'None':
                result = parse_side_effects(drugscom_link)
                dir = 'data\\side_effects_frequency_drugcom'
            elif rlsnet_link and rlsnet_link != 'None':
                print("rlsnet_link", rlsnet_link)
                result = get_side_effects_rlsnet(rlsnet_link)
                dir = 'data\\side_effects_frequency_rlsnet'

            if result:
                # Сохранить результаты в JSON-файл
                with open(f'{dir}\\{result['drug_name_en']}_side_effects.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
            elif rlsnet_link == 'None' and drugscom_link == 'None':
                print("Вообще нет:", drug_name_ru)
            else:
                print("Не найден:", row.get('drug_ru', '').strip())

            