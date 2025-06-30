"""Модуль загручика синонимов из json-файлов."""

import os
import json
import logging
from collections import OrderedDict

from django.conf import settings

from synonyms.utils.synonyms_loader import SynonymLoader
from synonyms.models import SynonymGroup, Synonym, SynonymStatus


logger = logging.getLogger('synonyms')


class InnerJSONSynonymLoader(SynonymLoader):
    """
    Загрузчик синонимов.

    Работает с нативным типом коллекций,
    из которых получается синонимы.
    """

    CLUSTERS = 'clusters'
    LABELS = 'labels'
    REPLACED = 'cluster_'
    REPLACING = 'Кластер_'
    IMPORT_PATH = 'exported_synonyms.json'
    UNDEFINITED = 'Не определено'

    def import_synonyms(self, clusters_data=None):
        """Импорт синонимов в БД."""

        SynonymStatus.objects.create(st_name=self.UNDEFINITED,
                                     st_code='#FF1493')

        clusters_data = clusters_data or open(
            os.path.join(settings.TXT_DB_PATH, self.IMPORT_PATH),
            'r',
            encoding='utf-8')
        clusters_data = json.load(clusters_data)
        for cluster in clusters_data[self.CLUSTERS].keys():
            group = SynonymGroup.objects.create(
                name=cluster.replace(self.REPLACED, self.REPLACING))
            for synonym in clusters_data[self.CLUSTERS][cluster][self.LABELS]:
                Synonym.objects.create(name=synonym, group=group)

    def export_synonyms(self):
        """Экспорт синонимов из БД в json-словаря."""
        clusters = OrderedDict()

        groups = SynonymGroup.objects.filter(
            synonyms__st_id__st_name=self.UNDEFINITED
        ).distinct().order_by('id')

        for index, group in enumerate(groups):
            synonyms = group.synonyms.filter(
                st_id__st_name=self.UNDEFINITED).values_list('name',
                                                             flat=True)
            clusters[f'cluster_{index}'] = {
                'labels': list(synonyms)
            }
        return json.dumps({'clusters': clusters}, ensure_ascii=False, indent=4)

    def export_synonyms_to_file(self, path=None):
        """Экспорт синонимов из БД в json-словаря."""
        path = path or os.path.join(settings.TXT_DB_PATH,
                                    'exported_synonyms.json')
        clusters = OrderedDict()

        for index, group in enumerate(SynonymGroup.objects.all()):
            synonyms = group.synonyms.values_list('name', flat=True)
            clusters[f'cluster_{index}'] = {
                'labels': list(synonyms)
            }

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(clusters, file, ensure_ascii=False, indent=4)
