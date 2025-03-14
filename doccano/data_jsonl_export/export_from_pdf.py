import fitz  # PyMuPDF
import re
import json

import os

import sys
sys.path.append("")

from convertors.normalize_text import normalize_text

DIR_PDF = "data\\Инструкции_ГРЛС_не_вкладыши_не_сканы"

def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as pdf:
        text = ""
        for page in pdf:
            text += page.get_text("text")  # Извлечение текста из каждой страницы
    return text

def extract_sections(name, text):
    sections = {}

    sections["drug"] = name

    # Извлекаем текст после "Фармакотерапевтическая группа" и до "Код АТХ"Фармакотерапевтическая
    # Фармакотерапевтическая группа 
    match_pharmacotherapeutic = re.search(r'Фармакотерапевтическая\s*группа\s*[:：]?\s*(.*?)\s*(Код АТХ|КОД ATX|Код ATX|КОД АТХ|Код АТX)', text, re.DOTALL)
    if match_pharmacotherapeutic:
        text_groups = match_pharmacotherapeutic.group(1).strip()
        text_groups = re.sub(r'\n', '', text_groups)
        sections["group"] = text_groups
    
    # Извлекаем текст от "Фармакодинамика" до "Показания к применению"
    match_pharmacodynamics = re.search(r'(Фармакологические\s*свойства|Фармакологическое\s*действие)(.*?)(Показания к применению|Показания к медицинскому применению)', text, re.DOTALL)
    if match_pharmacodynamics:
        text_main = match_pharmacodynamics.group(2).strip()
        text_main = normalize_text(text_main)
        text_main = re.sub(r'\n', ' ', text_main)
        text_main = re.sub(r'\s+', ' ', text_main)
        sections["text"] = text_main
    
    return sections

if __name__ == "__main__":

    drug_jsones = []

    for i, filename in enumerate(os.listdir(DIR_PDF)):
        if filename.endswith(".pdf"):
            name = filename.split(".")[0]
            # pdf_path = "document.pdf"  # Укажите путь к вашему PDF файлу
            pdf_path = f"{DIR_PDF}\\{filename}"
            # name = "Аллопуринол"
            extracted_text = extract_text_from_pdf(pdf_path)
            drug_sections = extract_sections(name, extracted_text)

            if drug_sections:
                drug_jsones.append(extract_sections(name, extracted_text))
            
    with open("data_jsonl_export\\extracted_data.json", "w", encoding="utf-8") as json_file:
        json.dump(drug_jsones, json_file, ensure_ascii=False, indent=4)
            
    print("Данные сохранены в extracted_data.json")
