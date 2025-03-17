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
    #   node_name: "аллопуринол",
    #   conditional_probability: {
    #       "0 0 1": P(i),
    #       "0 1 0": P(i+1), - порядок 0 и 1 соответствует порядку родилелей ноды в графу. Последний столбец для появления или не появления побочки
    #   }
    # }
    def __GenerateTables(self):
        tables = []
        idNullLevel = "" #Id нулевого уровня
        for node in self.graph["nodes"]:
            parentsCount = len(node["parents"]) # определили количество родителей
            if parentsCount==0: idNullLevel=node["id"]
            total = 2 ** parentsCount  # Общее количество комбинаций
            combinations = {}
            combinations["node_id"] = node["id"]
            combinations["node_name"] = node["name"]
            combinations["conditional_probability"] = {} #массив условных вероятностей
            combinations["convolution_table"] = {} #Свернутые таблицы
            for i in range(total):
                combination = []
                for j in range(parentsCount):
                    combination.append((i >> j) & 1)  # Извлекаем биты
                # combinations.append(combination[::-1])  # Разворачиваем, так как старшие биты идут первыми
                # Генерируем случайные вероятности и добавляем ключи в json (не появления побочки)
                if " ".join(map(str, combination[::-1])) == "":
                    combinations["conditional_probability"]["0"] =0
                    combinations["conditional_probability"]["1"] =1
                    combinations["convolution_table"]["0"] = 0
                    combinations["convolution_table"]["1"] = 1

                else: 
                    probability = random.random()
                    combinations["conditional_probability"][" ".join(map(str, combination[::-1]))+" 0"] = probability
                    combinations["conditional_probability"][" ".join(map(str, combination[::-1]))+" 1"] = 1 - probability

                    combinations["convolution_m"]={}
                    combinations["convolution_table"]["0"] = 0
                    combinations["convolution_table"]["1"] = 0


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
    
    # Добавляем свернутые таблички
    def __Add_node_convolution_m(self, node_id, convolution_m={}):
        for table in self.tables["tables"]:
            if(table["node_id"]==node_id): table["convolution_m"] = convolution_m
        # обновляем файл
        with open(self.graphFileTables, 'w', encoding='utf-8') as file:
                json.dump(self.tables, file, ensure_ascii=False, indent=4)

    # Добавление данных в свернутые таблицы и их нормализация
    def __Add_Convolution_table_Values(self, node_id, probability_0=0, probability_1=0):
        summ = probability_0+probability_1
        for table in self.tables["tables"]:
            if(table["node_id"]==node_id): 
                # Нормализация вероятностей
                # summ = probability_0+probability_1
                table["convolution_table"]["0"] = probability_0/summ
                table["convolution_table"]["1"] = probability_1/summ
         # обновляем файл
        with open(self.graphFileTables, 'w', encoding='utf-8') as file:
                json.dump(self.tables, file, ensure_ascii=False, indent=4)
        
        self.__WriteTrase(f"\nСвернутая таблица до нормировки")
        self.__WriteTrase_table({"0": probability_0, "1": probability_1})

        self.__WriteTrase(f"\nСвернутая таблица после нормировки")
        self.__WriteTrase_table({"0": probability_0/summ, "1": probability_1/summ})

        self.__WriteTrase("----------------------------------------------------------------------\n")

    def __WriteTrase(self, string=None):
        if string == None:
            with open('trase.txt', 'w',  encoding='utf-8') as file:
                file.write("Запись трассировки:\n")
                file.write("----------------------\n\n")
        else:
            with open('trase.txt', 'a',  encoding='utf-8') as file:
                file.write(string)
                file.write("\n")

    def __WriteTrase_table(self, data):
        for key, value in data.items():
            with open('trase.txt', 'a',  encoding='utf-8') as file:
                file.write(f"|\t{key}\t|\t{value}\t|")
                file.write("\n")

    def __Get_NameParents_Node(self, perent_id):
        for node in self.graph["nodes"]:
            if node["id"] == perent_id: return node["name"]


    # Вычисление совместных распределений для последующей свертки, чтобы вычислить вероятности появления побочек
    def __Сalculating_joint_distributions(self):
        self.__WriteTrase()
        for level in range(self.graph["maxLevel"]): # Перебураем уровни с 1 по максимальный
            self.__WriteTrase(f"Уровень - {level}")
            # Получем все узлы уровня
            levelNodes  = [node for node in self.graph["nodes"] if node["level"] == level]
            if(level>0): # Если не нулевой уровень
                # Считаем маргинализированные таблички
                for node in levelNodes:

                    self.__WriteTrase(f"Узел: - {node["name"]} ({node["id"]})")

                    convolution_m={} # Таблица для перемножения вероятностей
                    # Получаем таблицу узла
                    table = self.__Get_node_table(node["id"])
                    self.__WriteTrase(f"Таблица условных вероятностей")
                    self.__WriteTrase_table(table["conditional_probability"])

                    self.__WriteTrase(f"\nТаблицы родителей")
                    for i in range(len(node["parents"])):
                        self.__WriteTrase(f"Родитель {i+1} -{self.__Get_NameParents_Node(node["parents"][i])} - ({node["parents"][i]})")
                        parent_table = self.__Get_node_table(node["parents"][i])["convolution_table"]
                        self.__WriteTrase_table(parent_table)

                    # Проходим по всем строкам таблицы узла
                    for key, value in table["conditional_probability"].items():
                        states = key.split() #Получаем комбинации массива
                        probability = value #Вероятность после перемножения
                        
                        for i in range(len(node["parents"])):
                            parent_table = self.__Get_node_table(node["parents"][i])["convolution_table"]
                            if states[i] == '0': probability=probability*parent_table["0"]
                            else: probability=probability*parent_table["1"]
                            
                        convolution_m[key] = probability
                              
                    self.__Add_node_convolution_m(node["id"], convolution_m)
                    self.__WriteTrase(f"\nПеремноженная таблица вероятностей")
                    self.__WriteTrase_table(convolution_m)
                    
                    # делаем свертку таблицы
                    probability_0 = 0
                    probability_1 = 0
                    for key, value in table["convolution_m"].items():
                        states = key.split() #Получаем комбинации массива
                        if states[len(states)-1]=="0": probability_0 += value
                        else: probability_1 +=value

                    self.__Add_Convolution_table_Values(node["id"], probability_0, probability_1)
            else:
                self.__WriteTrase(f"Узел: - {levelNodes[0]["name"]} ({levelNodes[0]["id"]})")
                self.__WriteTrase(f"Таблица условных вероятностей")
                table = self.__Get_node_table(levelNodes[0]["id"])
                self.__WriteTrase_table(table["conditional_probability"])
                self.__WriteTrase("\n")
            
                


    # Обучение сети 
    def Learn(self):
        self.__GenerateTables() # Построение таблиц условных вероятностей с рандомным значением
        self.__Сalculating_joint_distributions() # Подсчет совместных распределений для каждой комбинации состояния радителей

       


        


bayesian = Bayesian("./drug_allopurinol.json")
bayesian.Learn()
