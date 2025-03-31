import json
import os
import re
import sys
import random
sys.path.append("")

from CustomPymorphy.CustomPymorphy import EnhancedMorphAnalyzer
from normalize_text import normalize_text
custom_morph = EnhancedMorphAnalyzer()

DIR_INPUT = "orlov_dataset"
DIR_OUTPUT = "processed_orlov_dataset"

# Можно попробовать взять:
# 0 - среднее
# 1- случайное из этого диапазона
STRATEGY = 0
if STRATEGY == 0:
    # Очень часто                               0.1 - 1
    # Часто                                     0.01 - 0.1,       
    # Нечасто                                   0.001 - 0.01,   
    # Редко                                     0.001 - 0.0001,   
    # Очень редко                               0 - 0.0001, 
    # Частота неизвестна                        0,
    # Данные о частоте, собранные после продажи 
    CONVERT_RATE = {
        "Очень часто": 0.55,
        "Часто": 0.055,
        "Нечасто": 0.0055,
        "Редко": 0.00055,
        "Очень редко": 0.00055,
        "Частота неизвестна": 0.000055,
    }
else:
    CONVERT_RATE = {
        "Очень часто":          round(random.uniform(0.1, 1), 6),
        "Часто":                round(random.uniform(0.01, 0.1), 6),
        "Нечасто":              round(random.uniform(0.001, 0.01), 6),
        "Редко":                round(random.uniform(0.0001, 0.001), 6),
        "Очень редко":          round(random.uniform(0, 0.0001), 6),
        "Частота неизвестна": 0,
    }

# freq_set = set()

# Функция для лемматизации текста
def lemmatize_text(text):
    words = re.findall(r'\w+|[^\w\s]', text)
    lemmatized = [custom_morph.parse(word)[0].normal_form for word in words]
    rezult_text = normalize_text(' '.join(lemmatized))
    return rezult_text

if __name__ == "__main__":

    for filename in os.listdir(DIR_INPUT):
        with open(f"{DIR_INPUT}\\{filename}", "r", encoding="utf-8") as file:
            data = json.load(file)
        # Преобразование структуры
        new_data = {
            "Название ЛС": data["Название ЛС"],
            "Побочные эффекты": {}
        }

        for category, effects in data["Побочные действия"].items():

            for frequency, effect_list in effects.items():
                # Костыль
                if frequency == "Часто неизвеста": frequency = "Частота неизвестна"
                if frequency == "Не часто": frequency = "Нечасто"
                if frequency == "Данные о частоте, собранные после продажи":
                    continue

                for effect in effect_list:
                    new_effect = lemmatize_text(effect.lower())
                    # new_frequency = CONVERT_RATE[frequency]
                    
                    new_data["Побочные эффекты"][new_effect] = frequency
        
        with open(f"{DIR_OUTPUT}\\{filename}", "w", encoding="utf-8") as newfile:
            json.dump(new_data, newfile, ensure_ascii=False, indent=4)

# print("freq_set:", freq_set)
        

    