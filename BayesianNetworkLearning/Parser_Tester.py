import networkx as nx
import pgmpy


from Parser.Parser import GraphParser 
import json


# Чтение файла с примером графа
filePath = "./Parser/testData/drug_0.json"
# Открываем и читаем JSON-файл
with open(filePath, 'r', encoding='utf-8') as file:
    data = json.load(file)  # Загружаем JSON в виде Python-словаря

# Пример использования
graphParser = GraphParser()
parseData = graphParser.Parse(data)

print(parseData)

