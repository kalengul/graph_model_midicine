"""Модуль загрузчика."""

import json
import os
import logging

from django.conf import settings
from django.db import connection

from contraindications.models import Contraindication
from drugs.models import Drug
from contraindications.utils.adapters import DrugAdapter, ContraAdapter
from graphs.utils.text_builder import TextBuilder


logger = logging.getLogger('contraindications')


class LoadAndBuildDrugContraindications:
    """Служебный класс для загрузки противопоказаний ЛС."""

    NAME = 'drug'
    CONTRAS = 'extracted_contraindication'
    PATH = os.path.join(settings.TXT_DB_PATH, 'extracted_data_not_all.json')
    CONT_DICT_PATH = os.path.join(settings.SYNONYM_PATH, 'dict_synonym_contraindications.json')

    def load_from_keys(self):
        """
        Загружает противопоказания из ключей JSON-словаря противопоказаний.
        Необходимо для загрузки противопоказаний, которых нет у текущих ЛС
        """
        
        try:
            with open(self.CONT_DICT_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Неожиданная ошибка при чтении {self.CONT_DICT_PATH}: {e}")
            return {}
        
        stats = {'created': 0, 'existed': 0, 'errors': 0}
        
        for contra_name in data.keys():
            try:
 
                contra_name = TextBuilder(contra_name).normalize().lower().strip().text
                
                # Создаем или получаем противопоказание
                obj, created = Contraindication.objects.get_or_create(
                    name__iexact=contra_name,
                    defaults={'name': contra_name}
                )
            
                if created:
                    stats['created'] += 1
                    logger.debug(f'Создано: {contra_name}')
                else:
                    stats['existed'] += 1
                    logger.debug(f'Существует: {contra_name}')
                    
            except Exception as e:
                stats['errors'] += 1
                logger.error(f'Ошибка при обработке "{contra_name}": {e}')
        
        logger.info(f'Итог: создано {stats["created"]}, существовало {stats["existed"]}, ошибок {stats["errors"]}')
        return stats

    def load(self, data=None):
        """Загрузка противопоказаний и связывание с ЛС."""
        logger.debug(f'СУБД: {connection.vendor}')
        if not data:
            with open(self.PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

        for item in data:
            drug_name = TextBuilder(item[self.NAME]).strip().text
            logger.debug(f'drug_name = {drug_name}')

            try:
                drug = Drug.objects.get(drug_name__iexact=drug_name)
            except Drug.DoesNotExist:
                logger.debug(f'Drug.DoesNotExist: {drug_name}')
                continue

            for name in item[self.CONTRAS]:
                name = TextBuilder(name).normalize().lower().strip().text
                try:
                    contraindication = Contraindication.objects.get(
                        name__iexact=name)
                    logger.debug(f'\tcont_name = {name} найдено')
                except Contraindication.DoesNotExist:
                    contraindication = Contraindication.objects.create(
                        name=name)
                    logger.debug(f'\tcont_name = {name} добавлено')
                drug.contraindications.add(contraindication)

    def download(self):
        """Выгрузка противопоказаний."""
        drug_with_contras = []
        for drug in Drug.objects.all():
            drug_with_contras.append({
                self.NAME: drug.drug_name,
                self.CONTRAS: [c.name for c in drug.contraindications.all()]
            })
        return drug_with_contras


class DrugContraindicationLoader:
    """Сервис для загрузки ЛС и противопоказаний."""

    def __init__(self, drug_key=None, contras_key=None):
        """Создание загрузчика."""
        self.drug_key = None if not drug_key else [drug_key]
        self.contras_key = None if not contras_key else [contras_key]

    def load_from_file(self, file_obj):
        """Загрузить данные из файла (file-like object)."""
        data = json.load(file_obj)
        self._process(data)

    def load_from_path(self, path):
        """Загрузить данные из файла по пути (для manage.py)."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self._process(data)

    def _process(self, data):
        for item in data:
            drug_name = DrugAdapter(item, self.drug_key).name
            drug_name = TextBuilder(drug_name).lower().strip().text
            drug, created = Drug.objects.get_or_create(
                drug_name__iexact=drug_name,
                defaults={"drug_name": drug_name},
            )

            for name in ContraAdapter(item, self.contras_key).contras:
                name = TextBuilder(name).lower().strip().text
                contraindication, _ = Contraindication.objects.get_or_create(
                    name__iexact=name, defaults={"name": name}
                )
                drug.contraindications.add(contraindication)
