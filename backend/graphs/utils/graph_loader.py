
"""Модуль загрузчика графов."""

import os
import json

from django.conf import settings

from graphs.models import Graph


DIR = os.path.join(settings.BASE_DIR, 'data/json_and_xml_graphs')


class JSONGraphLoader:
    """Загрузчик графов из JSON-файлов."""

    NAME = 'name'

    def load(self, count=None):
        """Загрузчик данных из JSON-файлов."""
        files = os.listdir(DIR)
        json_files = []
        xml_files = []

        for f in files:
            if f.endswith('.json'):
                json_files.append(f)
            elif f.endswith('.graphml'):
                xml_files.append(f)

        json_files.sort()
        xml_files.sort()

        if count:
            json_files = json_files[:count]
            xml_files = xml_files[:count]
        try:
            for file1, file2 in zip(json_files, xml_files):
                with open(os.path.join(DIR, file1), 'r',
                          encoding='utf-8') as f:
                    graph_json = json.load(f)

                with open(os.path.join(DIR, file2), 'r',
                          encoding='utf-8') as f:
                    graph_xml = f.read()

                name = '+'.join(graph_json.get(self.NAME))
                if name and Graph.objects.filter(name=name).count() == 0:
                    Graph.objects.create(name=name,
                                         graph_json=graph_json,
                                         graph_xml=graph_xml)

            print('Графы успешно загружены!')
        except Exception as error:
            print(f'Ошибка загрузки графов в БД! Ошибка: {error}')
