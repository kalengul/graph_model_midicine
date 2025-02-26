import networkx as nx


def gefx2yed(graph):
    # Чтение графа в формате .gefx
    input_file = "input_graph.gefx"
    graph = nx.read_gexf(input_file)

    # Если ваша библиотека добавляет дополнительную обработку, здесь можно её использовать:
    # graph = my_library.process_graph(graph)

    # Сохранение в формате .graphml
    output_file = "output_graph.graphml"
    nx.write_graphml(graph, output_file)

    print(f"Граф успешно сохранён в {output_file}")

    return

if __name__ == "__main__":

    # Чтение графа в формате .gefx
    input_file = "input_graph.gefx"
    graph = nx.read_gexf(input_file)

    