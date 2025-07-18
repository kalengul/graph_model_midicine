import json
import os

from create_graph import creat_praph
from merger_of_the_graphs import merge_graphs
from show_graph import plot_graph

directory = 'json_drug_without_chapter'
exclude_file = 'amiodaron.json'

amiadaron_path = os.path.join(directory, exclude_file)
if os.path.isfile(amiadaron_path):
    amiadaron_graph = creat_praph(amiadaron_path)


    for filename in os.listdir(directory):
        if filename == exclude_file:
            continue

        file_path_2 = os.path.join(directory, filename)

        if os.path.isfile(file_path_2):

            graph_2 = creat_praph(file_path_2)
            merged_graph = merge_graphs([amiadaron_graph, graph_2])

            plot_graph(merged_graph, name = f'{exclude_file}_{filename}', save = True, show = False, node_size=700, font_size=5)



