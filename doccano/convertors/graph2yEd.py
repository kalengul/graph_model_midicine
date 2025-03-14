import networkx as nx
import yedLib



def graph2yEd(graph, loaded_yed = False):
    graph_yed = yedLib.Graph()
    # Словарь для хранения идентификаторов узлов
    node_ids = {}
    node_set = set()

    # Добавление узлов
    for i, node in enumerate(graph.nodes()):

        if loaded_yed:
            label = graph.nodes[node].get("label", str(node))
            node_id = label
        else:
            name = graph.nodes[node].get("name", str(node))
            label = graph.nodes[node].get("label", str(node))
            node_id = f"{name}({label})"

        node_ids[node] = node_id
        if node_id not in node_set:
            graph_yed.add_node(node_id, shape="ellipse")
            node_set.add(node_id)
        else:
            print(f"Узел {node_id} уже существует, добавление пропущено.")


    # Добавление рёбер
    for i, (source, target, edge_data) in enumerate(graph.edges(data=True)):
        graph_yed.add_edge(node_ids[source], node_ids[target], arrowhead="standard")

    return graph_yed.get_graph()



if __name__ == "__main__":
    # Использование программы
    gefx_file = "data\\graph_data_gexf_edit\\drug_amlodipin_perindopril.gexf"
    graphml_file = "data\\graph_data_yed\\output.graphml"
    # Загрузка графа из .gefx файла
    graph = nx.read_gexf(gefx_file)
    xml_str = graph2yEd(gefx_file, graphml_file)
    # Записываем в файл
    with open(graphml_file, "w", encoding="utf-8") as f:
        f.write(xml_str)
    print(f"Конвертация завершена. Результат сохранён в {graphml_file}")
