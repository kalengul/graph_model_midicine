import uuid
import re
import sys
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import networkx as nx

from graphs.utils.parser import GraphParser
from graphs.utils import yedLib
from graphs.utils.custom_pymorphy.custom_pymorphy import EnhancedMorphAnalyzer


custom_morph = EnhancedMorphAnalyzer()
sys.path.append("")


class ProcessNxGraph():

    __TAGS_LIST = ['absorbtion', 'action', 'excretion', 'group',
                   'prot_link', 'mechanism', 'metabol', 'hormone',
                   'side_e', 'prepare', 'distribution']

    def __init__(self, morph_analyzer = custom_morph, side_e_dict = None, flag_debag = False):
        self.morph_analyzer = morph_analyzer
        self.flag_debag = flag_debag
        
        self.nodes_set = set()
        self.edges_set = set()

        self.map_side_e_dict = None
        if side_e_dict:
            self.map_side_e_dict = {side_e:side_104 for side_104, side_e in side_e_dict}

    @classmethod
    def get_tags_list(cls):
        """
        Геттер списка корректных тегов
        """
        return cls.__TAGS_LIST
    
    def split_by_bracket(self, text):
        """
        Отделение строки со скобкой на 2 строки
        """
        match = re.search(r"^(.*)\s*\(([^)]+)\)$", text)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return None, None
    
    def print_message(self, message, type_message = "DEBAG"):
        if type_message != "DEBAG" or self.flag_debag:
            print(f"     {type_message}:{message}")

    def extract_label_and_tag(self, G, node_id):
        """
        Отделение от названия узла сущность и её тег
        """
        node_label = G.nodes[node_id].get('label', node_id)
        return self.split_by_bracket(node_label)
    
    def get_label(G, node_id):
        """
        Получение label
        """
        return G.nodes[node_id].get('label', node_id)

    def find_prepare_nodes(self, G):
        """
        Поиск ЛС в графе
        """
        main_prepare = []

        # Поиск ЛС в графе
        for node in G.nodes():
            parents_id = G.predecessors(node)
            parent_tags = [self.extract_label_and_tag(G, parent_id)[1] for parent_id in parents_id]
            _, node_tag = self.extract_label_and_tag(G, node)
            if parents_id and any(tag == 'group' for tag in parent_tags) and node_tag == 'prepare':
                main_prepare.append(node)
        
        return main_prepare
    

    def concat_hanging_act_mech(self, G):
        """
        Этап 1: Конкатенация висячих узлов с тегами 'action'/'mechanism',
        имеющих потомка с тегом 'noun', и зацепление с главными веществами.
        """

        def find_hanging_act_mech(G):
            """
            Функция для поиска висячих узлов с тегами 'action' или 'mechanism',
            у которых нет входящих рёбер и хотя бы один потомок имеет тег 'noun'
            """

            return [
                    node for node in G.nodes()
                    if self.extract_label_and_tag(G, node)[1] in ('action', 'mechanism')
                    and not list(G.predecessors(node))
                    and any(self.extract_label_and_tag(G, child)[1] == 'noun' for child in G.successors(node))
                ]


        nodes_to_remove = set() # Список на удаление

        # Этап 1: Конкатенация висячих action/mechanism, имеющих потомка с тегом 'noun'
        hanging_act_mech = find_hanging_act_mech(G)

        while hanging_act_mech != []:
            for parent in hanging_act_mech:
                # Находим всех потомков с тегом 'noun' у родительского узла
                noun_children = [
                    child for child in list(G.successors(parent))
                    if self.extract_label_and_tag(G, child)[1] == 'noun'
                ]
                if any(self.extract_label_and_tag(G, child)[1] != 'noun' for child in list(G.successors(parent))):
                    self.print_message(f"{self.extract_label_and_tag(G, parent)} has been not noun in child", "WARNING")
                        
                if not noun_children:
                    raise RuntimeWarning("Висячая вершина не может иметь в потомках не noun")
            
                label_parent, tag_parent = self.extract_label_and_tag(G, parent)
                for child in noun_children:            
                    label_child, tag_child = self.extract_label_and_tag(G, child)

                    new_id = str(uuid.uuid4())
                    new_label = f"{label_parent} {label_child}({tag_parent})"
                    x, y = G.nodes[child].get("x", 0), G.nodes[child].get("y", 0)
                    G.add_node(new_id, label=new_label, x=x, y=y)

                    for prechild in list(G.predecessors(child)):
                        if prechild != parent:
                            G.add_edge(prechild, new_id)
                    
                    # Добавление рёбер от нового узла к потомкам узла-потомка
                    for grandchild in list(G.successors(child)):
                        G.add_edge(new_id, grandchild)

                    self.print_message(f"new_node:{new_label},"
                        f"->new_node: {list(G.predecessors(new_id))},"
                        f"new_node->: {list(G.successors(new_id))}")
                    
                    # Удаляем узел потомка с тегом 'noun'
                    nodes_to_remove.add(child)

                # Удаляем родительский узел
                G.remove_node(parent)
            
            # Пересчитываем список висячих action/mechanism узлов,
            # у которых есть потомок с тегом 'noun'
            hanging_act_mech = find_hanging_act_mech(G)

        # Удаление узлов после завершения обработки
        for remove_node in nodes_to_remove:
            if remove_node in G:
                G.remove_node(remove_node)

        # Зацепление с главными веществами для оставшихся висячих узлов с тегами 'action'/'mechanism',
        # у которых нет потомков с тегом 'noun'
        hanging_act_mech = [
            node for node in list(G.nodes())
            if self.extract_label_and_tag(G, node)[1] in ('action', 'mechanism') and G.in_degree(node) == 0
        ]
        prepare_nodes = self.find_prepare_nodes(G)
        for node in hanging_act_mech:
            for prepare in prepare_nodes:
                G.add_edge(prepare, node)

        return G
    
    def remove_remaining_noun(self, G):
        """
        Этап 2: Обход графа и удаление оставшихся узлов с тегом 'noun'.
        При этом происходит конкатенация родительских и дочерних узлов, если у дочернего тег 'noun'.
        """

        nodes_to_remove = set() # Список на удаление
        queue = list(G.nodes)   # Очередь для обработки узлов (динамически пополняется)
        i = 0                   # Индекс для отладки

        # Пока очередь из улов не кончилась
        while i < len(queue):
            node = queue[i]
            i += 1

            # Пропуск, если узел будет всё равно удалён
            if node in nodes_to_remove:
                continue       

            # node_label = G.nodes[node].get('label',node)
            node_name, node_tag = self.extract_label_and_tag(G, node)
            children = list(G.successors(node))

            if node_tag is None:
                self.print_message(f"Node:{node}, Node_name:{node_name}, Node_tag:{node_tag} is NONE", "WARNING")
                        
            for child in children:
                child_name, child_tag = self.extract_label_and_tag(G, child)
                x, y = G.nodes[child].get("x", 0), G.nodes[child].get("y", 0)
                if child_tag == "noun":
                    new_id = str(uuid.uuid4())
                    new_label = f"{node_name} {child_name}({node_tag})"

                    # Добавление нового узела и добавление его в очередь
                    G.add_node(new_id, label = new_label, x=x, y=y)
                    queue.append(new_id)  

                    # "Наследование" связей от текущего обрабатываемого узла
                    for parent in G.predecessors(node):
                        G.add_edge(parent, new_id)
                    for child_successor in G.successors(child):
                        G.add_edge(new_id, child_successor)

                    # Добавление в список удаления
                    nodes_to_remove.add(child)  

            # Если все дочерние узлы имеют тег 'noun', то родительский узел подлежит удалению
            child_tags = [self.extract_label_and_tag(G, child)[1] for child in children]
            if children and all(tag == 'noun' for tag in child_tags):
                nodes_to_remove.add(node)

        self.print_message(f"nodes_to_remove: {nodes_to_remove}")
        # Удаление узлов после завершения обработки
        for remove_node in nodes_to_remove:
            if remove_node in G:
                G.remove_node(remove_node)
        
        return G
    

    def collect_nodes_edges(self, G):
        """
        Сохнанить уникальные узлы и связи
        """

        main_prepare = self.find_main_prepare(G)
            
        # По всем узлам графа
        for node in G.nodes():
            label, tag = self.extract_label_and_tag(G, node)

            if tag not in ProcessNxGraph.get_tags_list():
                self.print_message(f"label:{label}, tag:{tag}, prepare:{main_prepare}", "INVALID TAG")
                continue

            if tag != "side_e" and not list(G.predecessors(node)) and not list(G.successors(node)):
                self.print_message(f"label:{label}, tag:{tag}, prepare:{main_prepare}", "INVALID NODE")
                continue

            self.nodes_set.add((label, tag))

        # По всем рёбрам
        for target, source in G.edges():
            label_t, tag_t = self.extract_label_and_tag(G, target)
            label_s, tag_s = self.extract_label_and_tag(G, source)

            if tag_t in ProcessNxGraph.get_tags_list() and tag_s in ProcessNxGraph.get_tags_list():
                self.edges_set.add((f"{label_t}({tag_t})", f"{label_s}({tag_s})"))

        return self.nodes_set, self.edges_set
    

    def link_isolated_side_e(self, G):
        """
        Прикрепление изолированных вершин побочек
        """

        G_new = G.copy()

        # Поиск вершин ЛС, к которым прикрепятся изолированные side_e
        main_prepare = self.find_prepare_nodes(G)

        # Добавление рёбер от узлов 'prepare' к 'side_e', у которых нет предков
        for node in G.nodes():
            _, node_tag = self.extract_label_and_tag(G, node)
            parents = list(G.predecessors(node))
            if not parents and node_tag == 'side_e':
                for prepare in main_prepare:
                    G_new.add_edge(prepare, node)

        return G_new


    def replacing_side_e_with_dict(self, G):
        """
        Замена побочек на побочки из словаря
        (Проверить)
        """

        if self.map_side_e_dict is None:
            self.print_message("Загрузите классификатор побочек.", type_message="ERROR")

        G_new = G.copy()

        # Добавление рёбер от узлов 'prepare' к 'side_e', у которых нет предков
        for node in G.nodes():
            node_label, node_tag = self.extract_label_and_tag(G, node)
            x, y = G.nodes[node].get("x", 0), G.nodes[node].get("y", 0)
            if node_tag == 'side_e':

                # Поиск подходящей замены на побочку согласно классификатору
                new_name = self.map_side_e_dict.get(node_label, node_label)

                # Добавить новый узел
                G_new.add_node(str(uuid.uuid4()), label=f"{node_label}({node_tag})", x=x, y=y)

                # Перенести входящие рёбра (u → A)
                for u, _ in list(G.in_edges(node)):
                    G_new.add_edge(u, new_name)

                # Перенести исходящие рёбра (A → v)
                for _, v in list(G.out_edges(node)):
                    G_new.add_edge(new_name, v)

            # Удалить старый узел
            G.remove_node(node)

        return G_new
    
    
    def merge_nodes_by_label(self, G: nx.Graph) -> nx.Graph:
        """
        Объединяет несколько вершин, сохраняя и объединяя мета-данные узлов.
        """
        # Группируем вершины по label
        label_to_nodes = {}
        for node_id, data in G.nodes(data=True):
            label = data.get('label')
            if label is not None:
                if label not in label_to_nodes:
                    label_to_nodes[label] = []
                label_to_nodes[label].append(node_id)

        new_G = nx.DiGraph()

        label_to_new_node = {}
        
        # Создаем новые вершины с объединёнными данными
        for label, nodes in label_to_nodes.items():
            if not nodes:
                continue
            # Вычислим средние координаты
            x_avg = sum(float(G.nodes[n]['x']) for n in nodes) / len(nodes)
            y_avg = sum(float(G.nodes[n]['y']) for n in nodes) / len(nodes)
            new_node_id = str(uuid.uuid4())
            new_G.add_node(new_node_id, label=label, x=str(x_avg), y=str(y_avg))
            label_to_new_node[label] = new_node_id

        # Добавляем рёбра с учётом новых ID
        for u, v in G.edges():
            label_u = G.nodes[u]['label']
            label_v = G.nodes[v]['label']
            new_u = label_to_new_node[label_u]
            new_v = label_to_new_node[label_v]
            if new_u != new_v:
                new_G.add_edge(new_u, new_v)

        return new_G

    def merge_graph_list_by_label(self, graph_list: list[nx.Graph]) -> nx.DiGraph:
        """
        Объединяет список графов в один, сливая вершины по 'label'.
        Каждая уникальная вершина получает UUID.
        """
        combined_G = nx.DiGraph()
        label_to_uuid = {}

        for G in graph_list:
            for _, data in G.nodes(data=True):
                label = data.get("label")
                if label is None:
                    continue  # Пропускаем узлы без label

                if label not in label_to_uuid:
                    node_uuid = str(uuid.uuid4())
                    combined_G.add_node(node_uuid, **data)
                    label_to_uuid[label] = node_uuid

            for u, v in G.edges():
                u_label = G.nodes[u].get("label")
                v_label = G.nodes[v].get("label")

                if u_label in label_to_uuid and v_label in label_to_uuid:
                    combined_G.add_edge(label_to_uuid[u_label], label_to_uuid[v_label])

        return combined_G
        
    @staticmethod
    def print_nodes(G):
        """
        Печать узлов
        """
        for node in G.nodes:
            print(node)

    @staticmethod
    def plot_graph(G, title: str = None):
        """
        Вывод графа на экран с использованием поля label в качестве подписей узлов
        и координат x, y, если они заданы. Поддерживается отображение заголовка.
        """
        # Проверяем, есть ли у всех узлов координаты
        has_coords = all('x' in G.nodes[n] and 'y' in G.nodes[n] for n in G.nodes)

        if has_coords:
            pos = {
                n: (float(G.nodes[n]['x']), -float(G.nodes[n]['y']))  # y инвертирован для лучшей визуализации
                for n in G.nodes
            }
        else:
            print("has_coords:", has_coords)
            pos = nx.shell_layout(G)

        labels = {
            node: G.nodes[node].get("label", node)
            for node in G.nodes
        }

        plt.figure(figsize=(8, 6))
        nx.draw(
            G, pos, labels=labels,
            with_labels=True,
            node_size=500,
            node_color="lightblue",
            font_size=6,
            edge_color="gray"
        )

        if title:
            plt.title(title)

        plt.axis('off')
        plt.tight_layout()
        plt.show()

    def graph2json(self, G, jsonpolina = True):
        """
        Обрабатывает граф в формате JSON.
        (проверить)
        """
        
        main_prepare = []           # Список узлов с тегом 'prepare', связанных с 'group'
        mapping = {}                # Сопоставление старых узлов с новыми UUID
        G_for_json = nx.DiGraph()
        
        # Обход всех узлов и создание новых узлов с UUID
        for node in G.nodes():
            new_id = str(uuid.uuid4())
            mapping[node] = new_id
            
            node_name, node_tag = self.extract_label_and_tag(G, node)
            if self.morph_analyzer:
                node_name = self.morph_analyzer.lemmatize_string(node_name)
            
            G_for_json.add_node(new_id, name=node_name, label=node_tag, weight=5)
            
            if any(self.extract_label_and_tag(G, p)[1] == 'group' for p in G.predecessors(node)) and node_tag == 'prepare':
                main_prepare.append(new_id)
                
        # Добавление рёбер между узлами, используя новые UUID
        for target, source in G.edges():
            target_uuid = mapping[target]
            source_uuid = mapping[source]
            G_for_json.add_edge(target_uuid, source_uuid)
        
        # Преобразование в JSON-формат
        data = nx.node_link_data(G_for_json, edges="links")
        data["name"] = [G_for_json.nodes[prepare].get("name", "") for prepare in main_prepare]

        if jsonpolina:
            parser = GraphParser()
            data = parser.jsonPolina(data)

        return data
    
    def save_nxGraph_to_yEd(self, G, path):
        """
        Сохранение графа в формате yEd
        """

        graph_yed = yedLib.Graph()
        # Словарь для хранения идентификаторов узлов
        node_ids = {}
        node_set = set()

        # Добавление узлов
        for i, node in enumerate(G.nodes()):

            node_id = str(uuid.uuid4())
            label = G.nodes[node].get("label", str(node))
            x = G.nodes[node].get("x", 0)
            y = G.nodes[node].get("y", 0)

            node_ids[node] = node_id
            if node_id not in node_set:
                graph_yed.add_node(node_id, label=label, x=x, y=y, shape="ellipse")
                node_set.add(node_id)
            else:
                print(f"Узел {node_id} уже существует, добавление пропущено.")

        # Добавление рёбер
        for i, (source, target, edge_data) in enumerate(G.edges(data=True)):
            graph_yed.add_edge(node_ids[source], node_ids[target], arrowhead="standard")

        xml_str = graph_yed.get_graph()

        with open(path, "w", encoding="utf-8") as f:
            f.write(xml_str)

        return xml_str

    def find_node_by_tag(self, G, find_tag):
        """
        Ищет уже существующие в графе узлы по заданному тегу
        """
        find_nodes = set()

        for node in G.nodes():
            _, tag = self.extract_label_and_tag(G, node)
            if tag == find_tag:
                find_nodes.add(node)

        return list(find_nodes)
    
    def convert_side_e_by_dict(self, G, side_e_dict):
        map_side_e_dict = {side_e:side_e_104
                            for side_e_104, side_e_list in side_e_dict.items()
                            for side_e in side_e_list}

        # Преобразование согласно словарю
        side_e_nodes = self.find_node_by_tag(G, find_tag="side_e")
        for node in side_e_nodes:
            label, _ = self.extract_label_and_tag(G, node)
            new_label = map_side_e_dict.get(label, label)
            G.nodes[node]["label"] = f"{new_label}(side_e)"

        # Объединение дублирующихся вершин
        G = self.merge_nodes_by_label(G)

        return G


    def load_graphml(self, xml_text: str):
        """
        Загружает .graphml файл и возвращает объект Graph с узлами и рёбрами
        с учётом пространств имён yEd/GraphML и лемматизации меток.
        """
        ET.register_namespace("", "http://graphml.graphdrawing.org/xmlns")
        ET.register_namespace("y", "http://www.yworks.com/xml/graphml")
        ns = {
            "g": "http://graphml.graphdrawing.org/xmlns",
            "y": "http://www.yworks.com/xml/graphml"
        }

        # Лемматизация названия вершин в графе согласно словарю
        if not self.morph_analyzer is None:
            # print("Nen")
            def repl(match):
                before, text, after = match.groups()
                label, tag = self.split_by_bracket(text)

                if not label or not tag:
                    return match.group(0)

                lemmatized = self.morph_analyzer.lemmatize_string(label)
                return f"{before}{lemmatized}({tag}){after}"

            xml_text = re.sub(
                r'(<y:NodeLabel[^>]*>)(.*?)(</y:NodeLabel>)',
                repl,
                xml_text,
                flags=re.DOTALL
            )

        root = ET.fromstring(xml_text)
        graph_el = root.find("g:graph", ns)

        G = nx.DiGraph()
        id_map = {}  # оригинальный id → uuid

        for node_el in graph_el.findall("g:node", ns):
            node_id = node_el.get("id")
            new_id = str(uuid.uuid4())  # новый уникальный id
            id_map[node_id] = new_id

            data_el = node_el.find("g:data[y:ShapeNode]", ns)
            if data_el is None:
                G.add_node(new_id)
                continue

            shape_el = data_el.find("y:ShapeNode", ns)
            geom = shape_el.find("y:Geometry", ns)

            x = float(geom.get("x", "0")) if geom is not None else 0.0
            y = float(geom.get("y", "0")) if geom is not None else 0.0

            label_el = shape_el.find("y:NodeLabel", ns)
            label = label_el.text if label_el is not None else node_id

            G.add_node(new_id, label=label, x=str(x), y=str(y))

        for edge_el in graph_el.findall("g:edge", ns):
            src = id_map.get(edge_el.get("source"))
            tgt = id_map.get(edge_el.get("target"))
            if src and tgt:
                G.add_edge(src, tgt)

        return G

if __name__ == "__main__":

    file_lizinopril = "process_yEd_graph\\data\\graph_yEd_raw_1\\drug_lizinopril.graphml"
    file_spironolacton = "process_yEd_graph\\data\\graph_yEd_raw_1\\drug_spironolakton.graphml"

    process_graph = ProcessNxGraph(custom_morph)

    G_lizinopril = process_graph.load_graphml(file_lizinopril)
    G_spironolacton = process_graph.load_graphml(file_spironolacton)

    # # Этап 1
    G_lizinopril = process_graph.concat_hanging_act_mech(G_lizinopril)
    G_spironolacton = process_graph.concat_hanging_act_mech(G_spironolacton)
    process_graph.plot_graph(G_spironolacton)
    # # Этап 2
    G_lizinopril = process_graph.remove_remaining_noun(G_lizinopril)
    G_spironolacton = process_graph.remove_remaining_noun(G_spironolacton)
    process_graph.plot_graph(G_spironolacton)
    # # Этап 3 
    G_lizinopril = process_graph.link_isolated_side_e(G_lizinopril)
    G_spironolacton = process_graph.link_isolated_side_e(G_spironolacton)


    DIR_TEST = "process_yEd_graph\\data\\test_graphs"

    process_graph.save_nxGraph_to_yEd(G_lizinopril, f"{DIR_TEST}\\lizinopril.graphml")
    process_graph.save_nxGraph_to_yEd(G_spironolacton, f"{DIR_TEST}\\spironolacton.graphml")

    merged_graph = process_graph.merge_graph_list_by_label([G_lizinopril, G_spironolacton])
    process_graph.save_nxGraph_to_yEd(merged_graph, f"{DIR_TEST}\\merged_lizinopril_spironolacton.graphml")
