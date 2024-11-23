import json
# import os
import sys
sys.path.append("")

from BIO2umf import BIO2umf 
from umf2html import umf2html 

def bio2html(input_file, output_file):
    
    # Читаем данные из JSON-файла
    with open(input_file, 'r', encoding='utf-8') as file:
        data_bio = json.load(file)

    data_umf = BIO2umf(data_bio)
    data_html = umf2html(data_umf)
    
    # Читаем данные из JSON-файла
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(data_html)

bio_file = "data_bio\\data_bio.json"
svg_file = "visualisation\\visualisation.svg"
if __name__ == "__main__":
    bio2html(bio_file, svg_file)