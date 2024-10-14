import os

import matplotlib.pyplot as plt
import matplotlib
import networkx as nx



def plot_graph(G, node_size=1000, font_size=7, name=None, save=False, show=True, dir=None, edge_label = False):

    # Создаем словарь сопоставления id с именами через генератор словаря
    labels = {node: data.get('name', node) for node, data in G.nodes(data=True)}

    # Вычисляем позиции узлов (расположение)
    pos = nx.spring_layout(G)  # Выбираем расположение узлов

    # Граф
    nx.draw(G, pos, with_labels=False, edge_color='gray', node_size=node_size, node_color='lightblue')

    # Имена узлов в центре вершин
    nx.draw_networkx_labels(G, pos, labels, font_size=font_size, verticalalignment='center', horizontalalignment='center')

    if edge_label:
        # Получение меток рёбер из атрибута 'label'и отображение меток рёбер
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    # Подпись
    if name:
        plt.title(f"Graph for {name}")

    # Создание директории, если её нет
    if dir is None:
        dir = os.path.join("full_pipeline", "plots")
    os.makedirs(dir, exist_ok=True)

    # Сохранение
    if save:

        # Используем 'Agg' для генерации графиков без отображения
        matplotlib.use('Agg')

        try:
            if name:
                filepath = os.path.join(dir, f'{name}.png')
            else:
                filepath = os.path.join(dir, "Graph for noname.png")
            plt.savefig(filepath)
            print(f"Graph saved as {filepath}")
        except Exception as e:
            print(f"Error saving graph: {e}")


    # Отображение графика, если это необходимо
    if show:
        plt.show()

    # Закрытие графика для освобождения памяти
    plt.close()
