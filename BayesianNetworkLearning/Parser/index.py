from Parser import GraphParser 
import json


# Чтение файла с примером графа
filePath = "./testData/drug_0.json"
# Открываем и читаем JSON-файл
with open(filePath, 'r', encoding='utf-8') as file:
    data = json.load(file)  # Загружаем JSON в виде Python-словаря

# Пример использования
graphParser = GraphParser()
parseData = graphParser.Parse(data)

print(parseData)

# Сохранение нового файла
# Сохраняем измененный JSON обратно в файл
filePath_output = "./testData/drug_0_Parse.json"
with open(filePath_output, 'w', encoding='utf-8') as file:
    json.dump(parseData, file, ensure_ascii=False, indent=4)