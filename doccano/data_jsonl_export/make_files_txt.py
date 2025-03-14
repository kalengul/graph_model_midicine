import json
import os

FILE_DIR = "data_jsonl_export"

def save_drugs_from_json(json_file):
    
    # Читаем JSON-файл
    with open(json_file, 'r', encoding='utf-8') as file:
        drugs = json.load(file)
    
    # Создаем файлы с названиями препаратов
    for drug in drugs:
        name = drug.get("drug", "Без имени")  # Убираем запрещенные символы
        text = drug.get("text", "")
        
        # file_path = f"{name}.txt"
        with open(f"{FILE_DIR}\\{name}.txt", 'w', encoding='utf-8') as f:
            f.write(text)
    
    print(f"Создано {len(drugs)} файлов")

# Использование
file_name = "extracted_data.json"
# file_name = "dataset_for_doccano.json"

json_file = f"{FILE_DIR}\\{file_name}"  # Укажите путь к вашему JSON-файлу
save_drugs_from_json(json_file)