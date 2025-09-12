"""Модуль загрузчика."""

import json
import os

from django.conf import settings

from contraindications.models import Contraindication
from drugs.models import Drug
from contraindications.utils.adapters import DrugAdapter, ContraAdapter


class LoadAndBuildDrugContraindications:
    """Служебный класс для загрузки противопоказаний ЛС."""

    NAME = 'drug'
    CONTRAS = 'extracted_contraindication'
    PATH = os.path.join(settings.TXT_DB_PATH, 'extracted_data_not_all.json')

    def load(self):
        """Загрузка противопоказаний и связывание с ЛС."""
        with open(self.PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            drug_name = item[self.NAME]
            try:
                drug = Drug.objects.get(drug_name__iexact=drug_name)
            except Drug.DoesNotExist:
                continue
            for name in item[self.CONTRAS]:
                try:
                    contraindication = Contraindication.objects.get(
                        name__iexact=name)
                except Contraindication.DoesNotExist:
                    contraindication = Contraindication.objects.create(
                        name=name)
                drug.contraindications.add(contraindication)


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
            drug, created = Drug.objects.get_or_create(
                drug_name__iexact=drug_name,
                defaults={"drug_name": drug_name},
            )

            for name in ContraAdapter(item, self.contras_key).contras:
                contraindication, _ = Contraindication.objects.get_or_create(
                    name__iexact=name, defaults={"name": name}
                )
                drug.contraindications.add(contraindication)
