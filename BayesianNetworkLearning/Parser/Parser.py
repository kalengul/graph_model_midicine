import uuid
import networkx as nx

class GraphParser:
    # Генерация IDs
    def __GetNewId(self):
       return str(uuid.uuid4())

    # Смена ID и выделение имени узла
    def __ChangeID(self, graphJSON):
        for node in graphJSON["nodes"]:
            # Исправляем ID на name и записываем уникальный ID
            name = node["id"]
            node["name"] = name
            new_id = self.__GetNewId()  # Генерируем новый UUID
            node["id"] = new_id

            # Заменяем source и target на новый id в links
            for link in graphJSON["links"]:
                if link["source"] == name:
                    link["source"] = node["id"]
                if link["target"] == name:
                    link["target"] = node["id"]

                # Добавляем уникальный ID для каждого link
                link["id"] = self.__GetNewId()
    
    # Выделение уровней узлов
    def __AssignLevels(self, graphJSON):
        node_levels = {}  # Словарь для хранения уровней узлов
        adjacency_list = {}  # Словарь для представления списка смежности

        # Заполнение списка смежности (ключ - target, значение - список source)
        for link in graphJSON['links']:
            source = link['source']
            target = link['target']
            if target not in adjacency_list:
                adjacency_list[target] = []
            adjacency_list[target].append(source)
        
        # Определение начальных узлов (те, которые ни разу не являются target)
        queue = []
        for node in graphJSON['nodes']:
            node_id = node['id']
            if not adjacency_list.get(node_id):  # Эквивалентно adjacencyList[nodeId].length === 0
                node_levels[node_id] = 0
                queue.append(node_id)
        
        # Обход графа в ширину (BFS)
        while queue:  # Эквивалентно queue.length > 0
            current = queue.pop(0)  # Эквивалентно queue.shift()
            current_level = node_levels[current]

            for link in graphJSON['links']:
                if link['source'] == current:
                    target = link['target']
                    if target not in node_levels: # Дополнительная проверка
                        node_levels[target] = 0
                    if node_levels[target] < current_level + 1:
                        node_levels[target] = current_level + 1
                        queue.append(target)

        # Добавление уровня узлам в исходный граф
        for node in graphJSON['nodes']:
            node['level'] = node_levels[node['id']]

        # Определение максимального уровня
        graphJSON['maxLevel'] = max(node_levels.values()) + 1  # Эквивалентно Math.max(...Object.values(nodeLevels))+1


    
    def Parse(self, graphJSON):
        # Проверяем наличие ключа isParse
        if not graphJSON.get("isParse", False):  # Если ключ отсутствует или равен False
            
            self.__ChangeID(graphJSON) # Смена ID
            self.__AssignLevels(graphJSON) # Выделение уровней узлов

            graphJSON["isParse"] = True

        return graphJSON

        # print(G.nodes[0])
        # print(self.__GetNewId())
        # print(graph)
