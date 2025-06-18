"""Модуль загручика синонимов из json-файлов."""

import json
import logging
from collections import OrderedDict

from django.conf import settings

from synonyms.utils.synonyms_loader import SynonymLoader
from synonyms.models import SynonymGroup, Synonym


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

    def import_synonyms(self, clusters_data):
        """Импорт синонимов в БД."""
        clusters_data = json.load(clusters_data)
        for cluster in clusters_data[self.CLUSTERS].keys():
            group = SynonymGroup.objects.create(
                name=cluster.replace(self.REPLACED, self.REPLACING))
            for synonym in clusters_data[self.CLUSTERS][cluster][self.LABELS]:
                Synonym.objects.create(name=synonym, group=group)

    def export_synonyms(self):
        """Экспорт синонимов из БД в json-словаря."""
        clusters = OrderedDict()

        # for index, group in enumerate(SynonymGroup.objects.all().order_by('id')):
        #     synonyms = group.synonyms.all().values_list('name', flat=True)
        #     clusters[f'cluster_{index}'] = {
        #         'labels': list(synonyms)
        #     }

        groups = SynonymGroup.objects.filter(synonyms__is_changed=True).distinct().order_by('id')

        for index, group in enumerate(groups):
            synonyms = group.synonyms.filter(is_changed=True).values_list('name', flat=True)
            clusters[f'cluster_{index}'] = {
                'labels': list(synonyms)
            }
        return json.dumps({'clusters': clusters}, ensure_ascii=False, indent=4)
