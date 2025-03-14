import requests
from bs4 import BeautifulSoup
# from bs4 import NavigableString
import re

def clean_effect(effect):
    return effect.lstrip("—").rstrip(".").strip().replace("\r\n", "").replace("\n", "")

def add_space_after_short_class(text):
    soup = BeautifulSoup(text, 'html.parser')
    # Находим все теги span с классом 'short js-short-word'
    for span in soup.find_all('span', class_='short js-short-word'):
        # Добавляем пробел после содержимого тега
        span.string = span.string + ' ' if span.string else span
    return str(soup)

def get_side_effects_rlsnet(url_part):
    url = "https://www.rlsnet.ru/"+url_part
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка {response.status_code}: Не удалось загрузить страницу")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')

    side_effects = {}
    
    # Извлечение наименования
    drug_name_section = soup.find('h2', {'id': 'deistvuiushhee-veshhestvo'})
    drug_name = drug_name_section.find_next().get_text(strip=True)
    drug_name = drug_name.replace('*', '').strip()
    # print(f"Извлечённое название: {drug_name}")

    # Ищем текст до скобок и текст внутри скобок
    match = re.match(r'([^(]+)(\(([^)]+)\))?', drug_name)
    
    # Если скобки есть, разделяем на две части
    if match:
        drug_name_ru = match.group(1).strip()  # Текст до скобок
        drug_name_en = match.group(3).strip() if match.group(3) else ""  # Текст внутри скобок (если есть)
        # print(f"До скобок: {drug_name_ru}, В скобках: {drug_name_en}")
    
    if drug_name_ru!= "":
        side_effects["drug_name_ru"] = drug_name_ru
    if drug_name_en != "":
        side_effects["drug_name_en"] = drug_name_en

    side_effects_section = soup.find('h2', {'id': 'pobocnye-deistviia'})
    
    if not side_effects_section:
        print("Не найдена секция с побочными эффектами")
        return None
    
    current_category = None
    
    for element in side_effects_section.find_all_next(['p', 'h2'], limit=100):

        if element.name == 'h2':
            break

        # print("text1:", element.get_text())

        # # Проверка на span с нужным классом
        # for span in element.find_all('span', class_='short js-short-word'):
        #     replacement_text = f' {span.get_text()} '  # Добавляем пробелы
        #     span.replace_with(replacement_text)
        #     print("text2:", element.get_text())

        # print("text3:", element.get_text())

        element_classes = element.get('class', [])
        # print(f"Element classes: {element_classes}")  # Проверка классов элемента
        
        if 'OPIS_POLE_ABZ' in element_classes or 'OPIS_DVFLD' in element_classes:
            text = element.get_text()
            # print("text:", text)
            # modified_text = add_space_after_short_class(html_text)
            if ':' in text:
                category, effects_text = map(str.strip, text.split(':', 1))
                if category not in side_effects:
                    side_effects[category] = {}
                
                effects = re.split(r';\s*', effects_text)
                for effect in effects:
                    effect = effect.strip()
                    match = re.match(r'([^—]+)\s*—\s*(.+)', effect)
                    if match:
                        freq, side_e = map(str.strip, match.groups())
                        side_effects[category].setdefault(freq, [])

                        # Удаляем все, что в скобках (включая сами скобки)
                        side_e = re.sub(r'\(.*?\)', '', side_e)
                        
                        # Разбиваем строку по запятой и очищаем лишние пробелы
                        side_e_list = [clean_effect(item.strip()) for item in side_e.split(',')]
                        side_effects[category][freq].append(side_e_list)
            elif current_category:
                side_effects[current_category].append(text)


        if 'Opis_Pole' in element_classes:
            italic = element.find('i')
            all_text_nodes = [t.strip() for t in element.find_all(string=True, recursive=True) if t.strip()]
            
            italic_text = italic.get_text(strip=True) if italic else ""
            normal_text_content = " ".join(t for t in all_text_nodes if italic_text not in t)
            
            has_italic = bool(italic_text)
            has_normal_text = bool(normal_text_content)
            
            # print(f"Found: italic='{italic_text}', normal='{normal_text_content}'")  # Отладочный вывод
            
            # Если только курсивный текст - это категория
            if has_italic and not has_normal_text:
                category = italic_text
                side_effects[category] = {}
            # Если есть и курсивный, и обычный текст - это частота и побочные эффекты
            elif has_italic and has_normal_text:
                side_e_list = [clean_effect(item.strip()) for item in normal_text_content.split(',')]
                side_effects[category][italic_text] = side_e_list

    return side_effects

# def main():

    
    # if side_effects:
    #     for category, frequencies in side_effects.items():
    #         print(f"{category}:")
    #         for freq, effects in frequencies.items():
    #             print(f"  {freq}:")
    #             for effect in effects:
    #                 print(f"    - {effect}")
    #         print()

if __name__ == "__main__":
    link = "drugs/trimetazidin-mv-akrixin-81468"
    side_effects = get_side_effects_rlsnet(link)
    print(side_effects)
