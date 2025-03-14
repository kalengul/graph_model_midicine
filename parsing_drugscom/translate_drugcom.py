import json
import csv
import os

def load_translation_dict(csv_path):
    """Загружает словарь переводов из CSV."""
    translation_dict = {}
    with open(csv_path, mode="r+", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            translation_dict[row["оригинал"]] = row["перевод"]
    return translation_dict

def translate_json(data, translation_dict):
    """Рекурсивно переводит строки в JSON, используя словарь переводов."""
    if isinstance(data, dict):
        return {translate_json(key, translation_dict): translate_json(value, translation_dict) for key, value in data.items()}
    elif isinstance(data, list):
        return [translate_json(item, translation_dict) for item in data]
    elif isinstance(data, str):
        return translation_dict.get(data, data)  # Заменяем, если есть перевод
    else:
        return data  # Оставляем неизменным числа, None и другие типы
    
def extract_strings(data, collected_strings=None):
    """Рекурсивно извлекает все строки из JSON."""
    if collected_strings is None:
        collected_strings = set()

    if isinstance(data, dict):
        for key, value in data.items():
            collected_strings.add(key)  # Сохраняем ключ
            extract_strings(value, collected_strings)
    elif isinstance(data, list):
        for item in data:
            extract_strings(item, collected_strings)
    elif isinstance(data, str):
        collected_strings.add(data)

    print(collected_strings)
    return collected_strings

def save_strings_to_csv(strings, csv_path):
    """Сохраняет все найденные строки в CSV с оригиналом и пустым переводом (если нет в словаре)."""
    with open(csv_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["оригинал"])  # Заголовок

        for string in sorted(strings):  # Сортируем для удобства
            cleaned_string = string.strip().lower()  # Убираем лишние пробелы и приводим к нижнему регистру
            if cleaned_string:  # Проверяем, что строка не пустая
                writer.writerow([cleaned_string])  # Записываем


if __name__ == "__main__":

    input_path = "data/side_effects_frequency_drugcom"
    output_path = "data/side_effects_frequency_drugcom_translate"
    words_path = "data/words.csv"
    csv_path = "data/translation.csv"

    """Обрабатывает все JSON-файлы в папке."""
    if not os.path.exists(output_path):
        os.makedirs(output_path)  # Создаем выходную папку, если её нет

    all_strings = set()

    # 1. Собираем строки из всех JSON-файлов
    for file_name in os.listdir(input_path):
        if file_name.endswith(".json"):
            with open(os.path.join(input_path, file_name), "r", encoding="utf-8") as file:
                json_data = json.load(file)
            all_strings.update(extract_strings(json_data))

    # 2. Сохраняем их в CSV
    save_strings_to_csv(all_strings, words_path)

    # 3. Загружаем переводы и применяем их ко всем файлам
    translation_dict = load_translation_dict(csv_path)
    

    for file_name in os.listdir(input_path):
        if file_name.endswith(".json"):
            input_file = os.path.join(input_path, file_name)
            output_file = os.path.join(output_path, file_name)

            with open(input_file, "r", encoding="utf-8") as file:
                json_data = json.load(file)

            translated_json = translate_json(json_data, translation_dict)

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(translated_json, file, ensure_ascii=False, indent=4)