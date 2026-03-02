import json
import os
import logging
from django.conf import settings

from ..models import Drug, DrugGroup, BannedDrugPair
from .banned_pairs_loader import JSONBannedPairLoader
from contraindications.utils.loader import LoadAndBuildDrugContraindications
from contraindications.models import Contraindication

logger = logging.getLogger(__name__)


class DrugDataLoader:
    """Загрузчик данных о ЛС."""

    def __init__(self, clear_before_load=True):
        self.clear_before_load = clear_before_load
        self.loader_banned = JSONBannedPairLoader()
        self.loader_contra = LoadAndBuildDrugContraindications()
        self.stats = {
            'drug_groups': 0,
            'drugs_updated':0,
            'banned_pairs': 0,
            'contraindications': 0
        }

    def load_all(self, data):
        """Загрузка всех данных."""
        if self.clear_before_load:
            Contraindication.objects.all().delete()
            self.loader_banned.clear_db()

        # Загрузка групп
        self._load_groups_and_link_drugs(data)

        # Загрузка запрещенных пар
        self._load_banned(data)

        # Загрузка противопоказаний
        self._load_contraindications(data)

        logger.info(f"Загрузка завершена: {self.stats}")
        return self.stats

    def _load_groups_and_link_drugs(self, data):
        """Загрузка групп и связывание с лекарствами."""
        
        for item in data:
            drug_name = item.get('drug', '').strip()
            group_name = item.get('global_group', '').strip()
            
            if not drug_name or not group_name:
                continue
            
            # Получаем или создаем группу
            group, created = DrugGroup.objects.get_or_create(
                dg_name__iexact=group_name,
                defaults={'dg_name': group_name}
            )
            if created:
                self.stats['drug_groups'] += 1
            
            # Обновляем лекарство
            updated = Drug.objects.filter(
                drug_name__iexact=drug_name
            ).exclude(
                drug_group=group
            ).update(drug_group=group)
            
            self.stats['drugs_updated'] += updated

    def _load_banned(self, data):
        """Загрузка запрещенных пар через существующий загрузчик."""
        # Сохраняем статистику
        old_count = BannedDrugPair.objects.count()
        
        # Используем существующий загрузчик
        self.loader_banned.load_to_db(data=data)
        
        # Считаем новые пары
        new_count = BannedDrugPair.objects.count()
        self.stats['banned_pairs'] = new_count - old_count

    def _load_contraindications(self, data):
        """Загрузка противопоказаний через существующий загрузчик."""
        # Сохраняем статистику
        old_count = Drug.contraindications.through.objects.count()
        
        # Используем существующий загрузчик
        self.loader_contra.load(data=data)
        
        # Считаем новые связи
        new_count = Drug.contraindications.through.objects.count()
        self.stats['contraindications'] = new_count - old_count