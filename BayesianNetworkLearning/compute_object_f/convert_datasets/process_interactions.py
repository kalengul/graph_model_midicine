import json
import os
import re
import sys
# import random
sys.path.append("")

from CustomPymorphy.CustomPymorphy import EnhancedMorphAnalyzer
from normalize_text import normalize_text
custom_morph = EnhancedMorphAnalyzer()


FILE_INPUT  = "interactions_dataset.json"
FILE_OUTPUT = "processed_interactions_dataset.json"

# Функция для лемматизации текста
def lemmatize_text(text):
    words = re.findall(r'\w+|[^\w\s]', text)
    lemmatized = [custom_morph.parse(word)[0].normal_form for word in words]
    rezult_text = normalize_text(' '.join(lemmatized))
    return rezult_text

if __name__ == "__main__":

    with open(FILE_INPUT, "r", encoding="utf-8") as file:
        data = json.load(file)

    # lemmatized_list_interact = [lemmatize_text(side_e)
    #                             for interaction in data
    #                             for side_e in interaction['взаимодействие']]

    # Преобразование структуры
    new_data = [
        {"drugs": [item['первое ЛС'], item['второе ЛС']],
        "interactions": [lemmatize_text(side_e)
                        for side_e in item['взаимодействие']]}
        for item in data
    ]

    with open(FILE_OUTPUT, "w", encoding="utf-8") as newfile:
        json.dump(new_data, newfile, ensure_ascii=False, indent=4)