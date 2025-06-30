import json

# Загрузка списка строк и префиксов из JSON-файлов
with open('json_files\\SideEffects_n_Word.json', 'r', encoding='utf-8-sig') as f:
    strings = json.load(f)

with open('json_files\\prefixes_sideeffect.json', 'r', encoding='utf-8-sig') as f:
    prefixes = json.load(f)['Prefix']

# Функция для проверки, начинается ли слово с одного из префиксов
def starts_with_prefix(word, prefixes):
    word_lower = word.lower()
    return any(word_lower.startswith(prefix.lower()) for prefix in prefixes)

# Используем множество для хранения уникальных строк
unique_filtered_strings = set()

# Удаление слов, которые начинаются с указанных префиксов, из каждой строки
for i in range(1,3):
    lines = strings[f'SideEffects_{i}_Word']
    # print(lines)
    for line in lines:
        words = line.split()
        filtered_words = [word for word in words if not starts_with_prefix(word, prefixes)]
        filtered_line = ' '.join(filtered_words)
        if filtered_line:  # Добавляем только непустые строки
            unique_filtered_strings.add(filtered_line)

# Преобразуем множество обратно в список
filtered_strings_list = list(unique_filtered_strings)

# Сортировка по количеству слов, а затем по алфавиту
filtered_strings_list.sort(key=lambda s: (len(s.split()), s))

# Сохранение обновленного списка строк в JSON-файл
with open('json_files\\filtered_strings_1.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_strings_list , f, ensure_ascii=False, indent=4)
