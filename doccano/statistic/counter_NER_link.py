import json

def count_relations(file_path):
    total_relations = 0
    total_ner = 0

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Считываем строку и преобразуем её в словарь
            record = json.loads(line.strip())

            print("relations в текущей строке:", record['relations'])
            
            # Убедимся, что поле "relations" существует и является списком
            if 'relations' in record and isinstance(record['relations'], list):
                total_relations += len(record['relations'])

            # Убедимся, что поле "entities" существует и является списком
            if 'entities' in record and isinstance(record['entities'], list):
                total_ner += len(record['entities'])

    return total_relations, total_ner

# Укажите путь к вашему файлу
file_path = 'data\\data_3.jsonl'
result_rel, result_ner = count_relations(file_path)
print(f"Общее количество элементов в поле 'relations': {result_rel}")
print(f"Общее количество ner в поле 'entities': {result_ner}")
