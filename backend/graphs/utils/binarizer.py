"""Модуль бинаризатора."""

from drugs.models import Drug
from graphs.models import Graph


class Binarizer:
    """Бинаризатор ID ЛС."""

    NAME = 'name'

    def _get_ids(self, name, graphs):
        """Получение id."""
        for node in graphs['nodes']:
            if node[self.NAME].lower() == name.lower():
                return node['id']

    def binarize(self, ids):
        """Бинаризация ID ЛС."""
        name2ids = {}
        for graph in Graph.objects.all():
            name = graph.name.lower()
            prepare_id = self._get_ids(name, graph.graph_json)
            if prepare_id:
                name2ids[name] = prepare_id

        bin_ids = dict.fromkeys([id for id in name2ids.values() if id != None], 0)

        for drug in Drug.objects.filter(id__in=ids):
            drug_name = drug.drug_name.lower()
            if drug_name in name2ids:
                bin_ids[name2ids[drug_name]] = 1

        return bin_ids
