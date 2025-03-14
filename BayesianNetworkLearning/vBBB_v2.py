from Parser.Parser import GraphParser 
import json
import os
import random
from pyvis.network import Network
from collections import defaultdict
from itertools import product

# Проверка графа на ацикличность

# Создание таблиц для входного графа

class Bayesian:
    def __init__(self, graphFilePath):
        with open(graphFilePath, 'r', encoding='utf-8') as file:
            data = json.load(file)  # Загружаем JSON в виде Python-словаря
        
        graphParser = GraphParser() #Создаем экземпляр парсера и парсим граф
        self.graph = graphParser.Parse(data) # (С удалением вершин без связей)

        # print(self.graph)

        # Сохранение файла с распарсенным графаом
        base, ext = os.path.splitext(graphFilePath)
        self.graphFile = graphFilePath
        self.graphFileParse =  f"{base}_Parse{ext}"
        self.graphFileTables = f"{base}_Tables{ext}"
        with open(self.graphFileParse, 'w', encoding='utf-8') as file:
            json.dump(self.graph, file, ensure_ascii=False, indent=4)

        self.tables = {}

    # Генерация таблиц графа с рандомными вероятностями 
    # Создаем json для каждой ноды
    # {
    #   node_id: id,
    #   "0 1": P(i),
    #   "1 0": P(i+1), - порядок 0 и 1 соответствует порядку родилелей ноды в графу. Вероятность указывается только если побочка появляется
    # }
    def __GenerateTables(self):
        tables = []
        for node in self.graph["nodes"]:
            parentsCount = len(node["parents"]) # определили количество родителей
            total = 2 ** parentsCount  # Общее количество комбинаций
            combinations = {}
            combinations["node_id"] = node["id"]
            combinations["node_name"] = node["name"]
            combinations["conditional_probability"] = {} #массив условных вероятностей
            for i in range(total):
                combination = []
                for j in range(parentsCount):
                    combination.append((i >> j) & 1)  # Извлекаем биты
                # combinations.append(combination[::-1])  # Разворачиваем, так как старшие биты идут первыми
                # Генерируем случайные вероятности и добавляем ключи в json
                if " ".join(map(str, combination[::-1])) == "":
                    combinations["conditional_probability"][" ".join(map(str, combination[::-1]))] =1
                else: combinations["conditional_probability"][" ".join(map(str, combination[::-1]))] = random.random()

            tables.append(combinations)

            # формируем итоговый JSON и сохраняем его в файл
            self.tables["tables"] = tables
            self.tables["graph"] = self.graphFileParse
            with open(self.graphFileTables, 'w', encoding='utf-8') as file:
                json.dump(self.tables, file, ensure_ascii=False, indent=4)
    
    # Строим все возможные цепочки от потомка к родителям
    def __build_chains(self, node_id, nodes, current_chain=None):
        if current_chain is None:
            current_chain = []

        # Добавляем текущий узел в цепочку
        current_chain.append(node_id)
        
        # Получаем узел по его ID
        current_node = next(node for node in nodes if node['id'] == node_id)
        
        # Если узел не имеет родителей, возвращаем цепочку
        if not current_node['parents']:
            yield current_chain
        else:
            # Иначе продолжаем строить цепочку по родителям
            for parent_id in current_node['parents']:
                yield from self.__build_chains(parent_id, nodes, current_chain.copy())

    # Получение таблицы для узла
    def __Get_node_table(self, node_id):
        for table in self.tables["tables"]:
            if(table["node_id"]==node_id): return table
        return None


    # Вычисление совместных распределений для последующей свертки, чтобы вычислить вероятности появления побочек
    def __Сalculating_joint_distributions(self):
        joint_distributions = {} # JSON для хранения априорной вероятности для каждого узла
         # вычисляем все вероятности когда побочный эффект возникает
        # for node in self.graphFileTables:
        #     joint_distributions = {} # Совместные распределения для каждой комбинации
        #     for cp in node["conditional_probability"]:

        # Строим все возможные цепочки от потомка к родителю
        all_chains = {}
        for node in self.graph["nodes"]:
            chains = list(self.__build_chains(node["id"], self.graph["nodes"]))
            # print(chains)
            all_chains[node['id']] = chains

        # Запись в тестовый файл
        with open("./all_chains.json", 'w', encoding='utf-8') as file:
                json.dump(all_chains, file, ensure_ascii=False, indent=4)

        # вычисляем все вероятности когда побочный эффект возникает
        for node in self.graph["nodes"]:
            node_table = self.__Get_node_table(node["id"]) # получение таблицы для узла


            

    
    # Обучение сети 
    def Learn(self):
        self.__GenerateTables() # Построение таблиц условных вероятностей с рандомным значением
        self.__Сalculating_joint_distributions() # Подсчет совместных распределений для каждой комбинации состояния радителей

       


        


bayesian = Bayesian("./drug_allopurinol.json")
bayesian.Learn()
