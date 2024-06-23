import requests
from bs4 import BeautifulSoup
import time
import json

import re

import sys
sys.path.append('./')

# # URL of the webpage
# url = "https://www.rlsnet.ru/active-substance/alprazolam-87"

# Function to remove invisible characters and clean text
def clean_text(text):
    if text:
        # Заменяем неразрывные пробелы на обычные пробелы
        text = text.replace('\xa0', ' ')
        # Удаляем HTML-теги
        text = re.sub(r'<.*?>', '', text)
        # Удаляем невидимые и управляющие символы
        text = re.sub(r'[\x00-\x1F\x7F-\x9F\u200B-\u200F\u2028\u2029\uFEFF]', '', text)
        text = re.sub(r'[\x00-\x1F\x7F-\x9F\u200B-\u200F\u2028\u2029\uFEFF]', '', text)
        # Удаляем лишние пробелы и возвращаем чистый текст
        return ' '.join(text.split())
    return text

# Function to add spaces around span elements with specific class
def replace_short_words_with_spaces(soup):
    for span in soup.find_all("span", class_="short js-short-word"):
        replacement_text = f' {span.get_text()} '
        span.replace_with(replacement_text)

def html_parse(url):

    if url == "None" or url == "???":
        return

    # Extract the last part of the URL
    last_part = url.split('/')[-1]

    # Extract the active substance name before the hyphen and join with '_'
    active_substance_parts = last_part.split('-')[:-1]
    active_substance = '_'.join(active_substance_parts)
    
    # Define headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Function to fetch the webpage
    def fetch_webpage(url, headers, retries=5, delay=5):
        for _ in range(retries):
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                print("Rate limit exceeded. Waiting before retrying...")
                time.sleep(delay)  # Wait before retrying
            else:
                print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
                break
        return None

    # Fetch the webpage with retries and delay
    html_content = fetch_webpage(url, headers)

    # Check if HTML content was successfully retrieved
    if html_content:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Helper function to safely get text from an element
        def get_text_by_id(soup, element_id):
            element = soup.find(id=element_id)
            if element:
                replace_short_words_with_spaces(soup)
                next_element = element.find_next("p")

                if not next_element:
                    return clean_text(element.find_next("p").get_text())

                grouped_text = []

                while next_element:
                    group_name_tag = next_element.find('i')

                    if group_name_tag:
                        group_name = group_name_tag.get_text()
                        description = ''.join(str(sibling) for sibling in group_name_tag.next_siblings if isinstance(sibling, str))
                        grouped_text.append({clean_text(group_name): clean_text(description)})
                    else:
                        grouped_text.append(clean_text(next_element.get_text()))

                    next_element = next_element.find_next_sibling("p")

                return grouped_text
            return None
        

        # Helper function to safely get text from an element
        def get_text_by_id_simple(soup, element_id):
            element = soup.find(id=element_id)
            if element:
                replace_short_words_with_spaces(soup)
                next_element = element.find_next("p")

                if not next_element:
                    return clean_text(element.find_next("p").get_text())

                grouped_text = []
                current_group = 'Общее'
                grouped_text.append({current_group: ''})

                while next_element:
                    group_name_tag = next_element.find('b')
                    if group_name_tag:
                        group_name = group_name_tag.get_text(strip=True)

                        # Если не эти подглавы
                        if group_name not in ['Механизм действия', 'Фармакодинамика', 'Фармакокинетика']:
                            next_element = next_element.find_next_sibling("p")
                            current_group = None
                            continue

                        current_group = clean_text(group_name)
                        grouped_text.append({current_group: ''})
                    elif current_group:
                        description = clean_text(next_element.get_text())
                        if grouped_text[-1][current_group]:
                            grouped_text[-1][current_group] += ' ' + description
                        else:
                            grouped_text[-1][current_group] = description
                    # else:
                    #     grouped_text.append(clean_text(next_element.get_text()))

                    next_element = next_element.find_next_sibling("p")

                return grouped_text
            return None


        # Extract data
        data = {
            "Фармакология": get_text_by_id_simple(soup, "pharmakologiya"),
            "противопоказания": get_text_by_id(soup, "protivopocazania"),
            "ограничения_к_применению": get_text_by_id(soup, "ogranichenie-k-primeneniu"),
            "применение_при_беременности_и_кормлении_грудью": get_text_by_id(soup, "primenenie-pri-beremennosti-i-kormlenie-grudiu"),
            "побочные_действия": get_text_by_id(soup, "pobochnie-deistvia"),
            "взаимодействие": get_text_by_id(soup, "vzaimodeistvie"),
            "передозировка": get_text_by_id(soup, "peredozirovka")
        }


    else:
        print("Failed to retrieve the webpage after retries.")

    # Print the extracted data
    # print("active_substance:", active_substance)
    # print(data)
    # print()

    # Convert the dictionary to a JSON object
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Save the JSON object to a file
    with open(f"./json_drug/{active_substance}.json", 'w', encoding='utf-8') as json_file:
        json_file.write(json_data)


# Открываем файл links.txt и читаем его построчно
with open('links.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Проходим по каждой строке и извлекаем название и ссылку
for line in lines:
    # Удаляем лишние пробелы и символы новой строки
    line = line.strip()
    
    # Разделяем строку по символу ":"
    if ':' in line:
        name, url = line.split(':', 1)  # Разделяем только по первому вхождению ':'
        
        # Удаляем лишние пробелы вокруг имени и ссылки
        name = name.strip()
        url = url.strip()

        html_parse(url)
