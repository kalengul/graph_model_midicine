import csv
import pymorphy3
from tqdm import tqdm

# Инициализация лемматизатора
morph = pymorphy3.MorphAnalyzer()

# Открываем исходный CSV-файл для чтения и новый файл для записи
infile_csv = "data_csv\\related_entities_without_zeros.csv"
outfile_csv = "data_csv\\related_entities_without_zeros_edit.csv"

with open(infile_csv, "r", encoding="utf-8") as infile, open(outfile_csv, "w", encoding="utf-8", newline="") as outfile:
    reader = csv.reader(infile, delimiter="\t")  # Предполагается, что CSV разделён табуляцией
    writer = csv.writer(outfile, delimiter="$")

    # Пропускаем первую строку (названия столбцов)
    headers = next(reader)
    writer.writerow(headers)

    # Используем множество для удаления дубликатов
    unique_rows = set()

    # Подсчитываем количество строк для tqdm
    total_lines = sum(1 for _ in infile)
    infile.seek(0)  # Возвращаем указатель на начало файла
    next(reader)    # Пропускаем строку с заголовками

    # Добавляем прогресс-бар
    for row in tqdm(reader, total=total_lines - 1, desc="Processing rows"):
        # Извлекаем первую и вторую сущности, убираем кавычки
        first_entity = row[0].split("\t")[0]
        second_entity = row[1].split("\t")[0]

        # Лемматизация сущностей (если требуется)
        # first_entity_lemmatized = " ".join([morph.parse(word)[0].normal_form for word in first_entity.split()])
        # second_entity_lemmatized = " ".join([morph.parse(word)[0].normal_form for word in second_entity.split()])

        # Формируем новую строку с разделителем $
        # first_entity_cleaned = first_entity_lemmatized.split(",")[0] + "$" + first_entity_lemmatized.split(",")[1]
        # second_entity_cleaned = second_entity_lemmatized.split(",")[0] + "$" + second_entity_lemmatized.split(",")[1]

        # Создаём запись и проверяем на уникальность
        result_row = (first_entity, second_entity, row[2])
        if result_row not in unique_rows:
            unique_rows.add(result_row)
            writer.writerow(result_row)
