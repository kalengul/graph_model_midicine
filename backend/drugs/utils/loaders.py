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

    @abstractmethod
    def _export_drugs(self):
        """Экспорт ЛС."""

    @abstractmethod
    def _export_side_effects(self):
        """Экспорт ПД."""

    @abstractmethod
    def _export_rangs(self):
        """Экспорт рангов."""

    def export_from_db(self):
        """Экспорт из БД."""
        self._export_drugs()
        self._export_side_effects()
        self._export_rangs()


class ExcelLoader(Loader):
    """Загрузчик из excel-файлов."""

    EXCEL_PATH = os.path.join(settings.TXT_DB_PATH,
                              'Таблица_для_программы_по_побочным_эффектам.xlsx')
    EXPORT_PATH = os.path.join(settings.TXT_DB_PATH, 'exported_data.xlsx')
    BASE_SHEET = 'Лист2'
    SIDE_EFFECTS_SHEET = 'Лист1'
    # MILD = 1
    # MODERATE = 29
    # SEVERE = 70

    def __init__(self, path=None):
        """
        Конструктор.
        
        Принимает путь к файл с данными.
        Если путь не указан, загружается из файл по умолчания.
        """
        if path:
            self.path = path
        else:
            self.path = self.EXCEL_PATH

    def _load_drugs(self):
        """Загрузка ЛС."""
        df = pd.read_excel(self.path, sheet_name=self.BASE_SHEET)

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
        df = pd.read_excel(self.path,
                           sheet_name=self.SIDE_EFFECTS_SHEET
                        #    skiprows=[self.MILD, self.MODERATE, self.SEVERE]
                           )        
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
        df = pd.read_excel(self.path, sheet_name=self.BASE_SHEET)

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

    def _export_drugs(self):
        """Экспорт ЛС."""
        drugs = Drug.objects.order_by('index')
        numbers = [drug.index for drug in drugs]
        drug_names = [drug.drug_name for drug in drugs]
        self.drugs_df = pd.DataFrame(
            {
                'n': numbers,
                '': drug_names
            }
        )

    def _export_side_effects(self):
        """Экспорт ПД."""
        side_effects = SideEffect.objects.order_by('index')
        numbers = [side_effect.index for side_effect in side_effects]
        side_effect_names = [side_effect.se_name for side_effect in side_effects]
        weights = [side_effect.weight for side_effect in side_effects]

        self.side_effects_df = pd.DataFrame(
            {
                '№': numbers,
                'эффект': side_effect_names,
                'ранг': weights
            }
        )

        # with pd.ExcelWriter() as writer:
        #     df.to_excel(writer, sheet_name='ПД', index=False)

    def _export_rangs(self):
        """Экспорт рангов."""
        side_effects = SideEffect.objects.order_by('index')
        drugs = Drug.objects.order_by('index')
        column_headers = [se.index for se in side_effects]

        # data_dict = {}
        rows = []

        for drug in drugs:
            row = []
            for effect in side_effects:
                try:
                    dse = DrugSideEffect.objects.get(drug=drug, side_effect=effect)
                    row.append(dse.rang_base)  # или другой ранг
                except DrugSideEffect.DoesNotExist:
                    logger.info('Нет таблицы рангов')
            rows.append(row) # или drug.drug_name

        df = pd.DataFrame(rows, columns=column_headers)

        # print(f'df = {df}')

        with pd.ExcelWriter(self.EXPORT_PATH, engine='openpyxl') as writer:
            self.side_effects_df.to_excel(writer,
                                          sheet_name='Лист1',
                                          index=False,
                                          startcol=0)
            df_combined = pd.concat([self.drugs_df, df], ignore_index=True, axis=1)
            # print(f'df_combined = {df_combined}')
            df_combined.to_excel(writer, sheet_name='Лист2', index=False)

    def export_from_db(self):
        """Экспорт из БД."""
        open(self.EXPORT_PATH, 'w', encoding='utf-8').close()
        super().export_from_db()
