"""Модуль слияния графов."""

import json
import sys
from typing import Any

from django.conf import settings

from graphs.models import Graph
from graphs.utils.process_nx_graph import ProcessNxGraph


class Merger:
    """Слиятель графов."""

    PATH_SIDE_E_DICT = (f"{settings.BASE_DIR}\\graphs\\utils\\"
                        "data\\side_e_synonim_dict_all.json")

    def merge(self, ids: list[int]) -> Any:
        processor = ProcessNxGraph()
        graphs=[]

        with open(self.PATH_SIDE_E_DICT, "r", encoding="utf-8") as file:
            side_e_dict = json.load(file)[0]

        for id in ids:
            graph = Graph.objects.filter(id=id).first()
            if not graph:
                continue
            G = processor.load_graphml(graph.graph_xml)
            G = processor.concat_hanging_act_mech(G)
            G = processor.remove_remaining_noun(G)
            G = processor.link_isolated_side_e(G)
            G = processor.convert_side_e_by_dict(G, side_e_dict)
            graphs.append(G)

        merged_graphs = processor.merge_graph_list_by_label(graphs)
        print(merged_graphs)

        return processor.graph2json(merged_graphs)


def main():
    """Точка входна в программу."""    
    try:
        ids = [int(id) for id in sys.argv[1:]]
        Merger().merge(ids)
        print('Графы слиты успешно!')
    except ValueError:
        print("Все аргументы должны быть числами (id графов)")
        return
    except Exception as error:
        print(f'При слиянии графов произошла ошибка! Ошибка: {error}')


if __name__ == '__main__':
    main()
