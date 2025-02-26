import json
# import os
import sys
sys.path.append("")

from BIO2umf import BIO2umf_d 
from umf2html import umf2html 

def bio2html(input_file, output_file):
    
    # Читаем данные из JSON-файла
    with open(input_file, 'r', encoding='utf-8') as file:
        data_bio = json.load(file)

    # umf_list = []
    # for sent in data_bio:
    #     umf_list.extend(BIO2umf_d(sent['tokens'], sent['tags']))

    umf_list = BIO2umf_d(data_bio)
    print(umf_list)

    data_html = umf2html(umf_list)
    
    # Читаем данные из JSON-файла
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(data_html)

bio_file = "data_bio\\Perindopril_for_state.json"
svg_file = "visualisation\\Perindopril_for_state.svg"
if __name__ == "__main__":
    bio2html(bio_file, svg_file)