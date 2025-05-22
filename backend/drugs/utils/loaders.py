"""Модуль абстрактный загрузчик."""

import os
import logging
from abc import ABC, abstractmethod

import pandas as pd

from django.conf import settings

from ..models import (DrugGroup,
                      Drug,
                      DrugSideEffect,
                      SideEffect)

logger = logging.getLogger('drugs')


class Loader(ABC):
    """Абстрактный загрузчик."""

    @abstractmethod
    def _load_drugs(self):
        """Загрузка ЛС."""

    @abstractmethod
    def _load_side_effects(self):
        """Загрузка ПД."""

    @abstractmethod
    def _load_ranks(self):
        """Загрузка рангов."""

    def load_to_db(self):
        """Загрузка в БД всех данных."""
        self._load_drugs()
        self._load_side_effects()
        self._load_ranks()


class ExcelLoader(Loader):
    """Загрузчик из excel-файлов."""

    EXCEL_PATH = os.path.join(settings.TXT_DB_PATH, 'Базовые эффекты.xlsx')
    BASE_SHEET = 'Лист2'
    SIDE_EFFECTS_SHEET = 'Лист1'
    MILD = 1
    MODERATE = 29
    SEVERE = 70

    def _load_drugs(self):
        """Загрузка ЛС."""
        df = pd.read_excel(self.EXCEL_PATH, sheet_name=self.BASE_SHEET)

        try:
            logger.info('Загрузка ЛС началась')
            group, _ = DrugGroup.objects.get_or_create(
                id=1,
                defaults={'dg_name': 'Общая группа'})
            for drug in df.iloc[:, 1].to_list():
                Drug.objects.create(drug_name=drug.strip(),
                                    drug_group=group)
            logger.info(f'Загружено ЛС: {Drug.objects.count()}')
        except Exception as error:
            raise Exception(f'Проблема с загрузкой ЛС: {error}')

    def _load_side_effects(self):
        """Загрузка ПД."""        
        df = pd.read_excel(self.EXCEL_PATH,
                           sheet_name=self.SIDE_EFFECTS_SHEET,
                           skiprows=[self.MILD, self.MODERATE, self.SEVERE])        
        try:
            logger.info('Загрузка побочных действий началась')
            for _, side_effect, weight in list(df.itertuples(index=False, name=None)):
                SideEffect.objects.create(
                    se_name=side_effect.strip(),
                    weight=weight)
            logger.info(f'Загружено побочных действий: {SideEffect.objects.count()}')
        except Exception as error:
            raise Exception(f'Проблема с загрузкой {error}')

    def _load_ranks(self):
        """Загрузка рангов."""
        df = pd.read_excel(self.EXCEL_PATH, sheet_name=self.BASE_SHEET)

        df = df.iloc[:, 2:]
        df = df.reset_index(drop=True)
        df = df.fillna(0)

        drugs = list(Drug.objects.order_by('id'))
        effects = list(SideEffect.objects.order_by('id'))

        logger.debug(f'Число ЛС = {len(drugs)}')
        logger.debug(f'Число ПД = {len(effects)}')
        logger.debug(f'Число рангов = {df.shape}')

        assert df.shape == (len(drugs), len(effects)), (
            "Размерность рангов не совпадает!")

        bulk = []

        idx = 0
        for i, drug in enumerate(drugs):
            for j, effect in enumerate(effects):
                bulk.append(
                    DrugSideEffect(
                    drug=drug,
                    side_effect=effect,
                    rang_base=df.iloc[i, j]
                    )
                )
                idx += 1
                logger.info(f"Прогресс: {idx}/{len(effects)*len(drugs)} итераций")

        DrugSideEffect.objects.bulk_create(bulk, batch_size=500)

        logger.info(f'Загружено рангов: {idx}') 

    def load_to_db(self):
        """Загрузка в БД всех данных."""
        return super().load_to_db()
