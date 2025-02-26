import json
import re
import fitz  # PyMuPDF

def extract_text_between(pdf_path, start_bold, end_bold):
    doc = fitz.open(pdf_path)
    extracted_text = ""
    capture = False
    frequency_keywords = {"очень часто", "часто", "нечасто", "редко", "очень редко", "частота неизвестна"}
    temp_text = ""
    start_side_effect_flag = False
    enumeration_active = False
    
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    is_bold = "bold" in span["font"].lower()
                    is_italic = "italic" in span["font"].lower() or "oblique" in span["font"].lower()
                    
                    if is_bold and text.lower() == start_bold.lower():
                        capture = True
                        extracted_text = ""  # Очистить накопленный текст, чтобы начать новую секцию
                    elif is_bold and text.lower() == end_bold.lower():
                        capture = False
                    
                    if capture:
                        if is_italic:
                            if start_side_effect_flag:
                                extracted_text += temp_text
                                temp_text = ""
                                extracted_text += f"_{text}_ "
                            else:
                                temp_text = ""
                                extracted_text += text
                                start_side_effect_flag = True
                        else:
                            # Если начинается 
                            if text and (text[0].islower() or text.startswith(tuple(frequency_keywords))):
                                temp_text += f"{text} "
                                enumeration_active = True
                            elif enumeration_active:
                                break

    extracted_text += temp_text
    return extracted_text.strip()

def extract_key_value_pairs(text):
    key_value_dict = {}
    key = None
    
    for match in re.finditer(r'_(.*?)_', text):  # Ищем курсивный текст
        if key:
            key_value_dict[key] = text[:match.start()].strip().split(", ")
        key = match.group(1)
        text = text[match.end():]
    
    if key:
        key_value_dict[key] = text.strip().split(", ")
    
    return key_value_dict

def main(pdf_path, output_json):
    text = extract_text_between(pdf_path, "Побочное действие", "Передозировка")

    print("text:", text)
    data = extract_key_value_pairs(text)
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Данные сохранены в {output_json}")

# Пример использования
if __name__ == "__main__":

    drug_name = "Нитроглицерин"
    main(f"data\\Инструкции ГРЛС\\{drug_name}.pdf", f"data\\side_effects_frequency_grls\\{drug_name}.json")  
