import networkx as nx
import xml.etree.ElementTree as ET
from xml.dom import minidom

def graph2drawio(graph):

    # Применение алгоритма force-directed (spring layout)
    pos = nx.spring_layout(graph)  # Получение координат вершин

    # Создание корневого элемента для файла Draw.io
    mxfile = ET.Element("mxfile")
    diagram = ET.SubElement(mxfile, "diagram", name="Page-1")
    mxGraphModel = ET.SubElement(diagram, "mxGraphModel")
    root = ET.SubElement(mxGraphModel, "root")

    # Добавление базовых элементов Draw.io
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    # Словарь для хранения идентификаторов узлов
    node_ids = {}

    # Добавление узлов графа в Draw.io
    for i, node in enumerate(graph.nodes()):
        node_id = str(i + 2)  # Уникальный идентификатор для узла
        node_ids[node] = node_id
        node_data = graph.nodes[node]

        # Получение координат узла из алгоритма spring_layout
        x, y = pos[node]

        # Добавление узла как элемента mxCell
        mx_cell = ET.SubElement(
            root,
            "mxCell",
            id=node_id,
            value=f"{node_data.get("name", node)}({node_data.get("label", node)})",
            style="shape=ellipse;fillColor=#dae8fc;strokeColor=#6c8ebf;",
            vertex="1",
            parent="1"
        )
        geometry = ET.SubElement(mx_cell, "mxGeometry")
        geometry.set("x", str(x * 1000))  # Умножаем для масштабирования
        geometry.set("y", str(y * 1000))  # Умножаем для масштабирования
        geometry.set("width", "80")
        geometry.set("height", "40")
        geometry.set("as", "geometry")

    # Добавление рёбер графа в Draw.io
    for i, (source, target, edge_data) in enumerate(graph.edges(data=True)):
        edge_id = str(i + len(node_ids) + 2)  # Уникальный идентификатор для рёбер
        label = edge_data.get("label", "")

        # Создание рёберного элемента с прямыми рёбрами
        mx_cell = ET.SubElement(
            root,
            "mxCell",
            id=edge_id,
            value=label,
            style="edgeStyle=straightEdgeStyle;rounded=0;html=1;",
            edge="1",
            parent="1",
            source=node_ids[source],
            target=node_ids[target]
        )
        # Создание геометрии рёбер
        geometry = ET.SubElement(mx_cell, "mxGeometry")
        geometry.set("as", "geometry")

    # Сохранение в файл с отступами
    tree = ET.ElementTree(mxfile)
    # Преобразуем в строку с отступами
    xml_str = minidom.parseString(ET.tostring(mxfile, encoding="utf-8")).toprettyxml(indent="    ")

    return  xml_str

if __name__ == "__main__":
    # Использование программы
    gefx_file = "data\\graph_data_gexf_edit\\drug_amlodipin_perindopril.gexf"
    drawio_file = "data\\graph_data_drawio\\drug_amlodipin_perindopril.drawio"

    # Загрузка графа из .gefx файла
    graph = nx.read_gexf(gefx_file)

    drawio = graph2drawio(gefx_file, drawio_file)

    # Записываем в файл
    with open(drawio_file, "w", encoding="utf-8") as f:
        f.write(drawio)

    print(f"Конвертация завершена. Результат сохранён в {drawio_file}")