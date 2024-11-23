import json
import os
import sys
sys.path.append("")

from BIO2umf    import BIO2umf
from umf2jsonl  import umf2jsonl

def prepare_bio_folder(input_folder, output_folder):

    # Проходим по каждому JSON-файлу
    for filename in os.listdir(input_folder):

        # Читаем данные из JSON-файла
        with open(f"{input_folder}\\{filename}", 'r', encoding='utf-8') as file:
            data_bio = json.load(file)

        # Ковернтация
        data_umf = BIO2umf(data_bio)
        data_jsonl = umf2jsonl(data_umf)

        # Запись
        new_file_name = filename.replace('.json', '_converted.jsonl')
        with open(f"{output_folder}\\{new_file_name}", 'w', encoding='utf-8') as f:
            json.dump(data_jsonl, f, ensure_ascii=False)



if __name__ == "__main__":

    bio_folder = "data_bio"
    json_folder = "data_jsonl_import"
    prepare_bio_folder(bio_folder, json_folder)
