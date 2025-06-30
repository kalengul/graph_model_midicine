import json
import sys

sys.path.append("")

from my_lib.lemmatize import lemmatize_sentence, stem_sentence

# Загрузка JSON данных
with open(f'json_files\\Dictionary.json', 'r', encoding='utf-8-sig') as file:
    json_data = json.load(file)


# Применение стемминга к каждому побочному эффекту
json_data['SideEffects'] = [stem_sentence(effect) for effect in json_data['SideEffects']]


# Вывод результатов
with open(f'json_files\\Stamming.json', 'w', encoding='utf-8') as file:
    json.dump(json_data, file, ensure_ascii=False, indent=4)