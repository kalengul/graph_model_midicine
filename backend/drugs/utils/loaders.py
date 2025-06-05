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
                              'Список побочных эффектов edit_2.xlsx')
    EXPORT_PATH = os.path.join(settings.TXT_DB_PATH, 'exported_data.xlsx')
    RANKS_SHEET = 'Common'
    SIDE_EFFECTS_SHEET = 'Side_e'
    DRUGS_SHEET = 'Drugs'
    DRUG_SIDE_EFFECT = 'ЛС/ПЭ'
    NUMBER_COLUMN = '№'
    DRUG_COLUMN = 'ЛС'
    EFFECT_COLUMN = 'эффект'
    EFFECT_COLUMN_EN = 'эффект_en'
    RANK_COLUMN = 'ранг'
    EXPORT_DATE_SHEET = 'Export Date'


    def __init__(self, import_path=None, export_path=None):
        """
        Конструктор.
        
        Принимает путь к файл с данными.
        Если путь не указан, загружается из файл по умолчания.
        """
        if import_path:
            self.import_path = import_path
        else:
            self.import_path = self.EXCEL_PATH
        if export_path:
            self.export_path = export_path
        else:
            self.export_path = self.EXPORT_PATH

    def _check_excel_file(self):
        """Проверка корректности excel-файла."""
        excel_file = pd.ExcelFile(self.import_path)

        def check_sheets():
            """Проверка листов."""
            return all([
                self.DRUGS_SHEET in excel_file.sheet_names,
                self.SIDE_EFFECTS_SHEET in excel_file.sheet_names,
                self.RANKS_SHEET in excel_file.sheet_names
            ])

        def check_tables():
            """Проверка таблиц."""
            colunms = []
            for _, col in pd.read_excel(self.import_path, sheet_name=None).items():
                colunms.extend(col.columns)
            return all(elem in colunms for elem in [
                self.NUMBER_COLUMN,
                self.DRUG_COLUMN,
                self.EFFECT_COLUMN,
                self.RANK_COLUMN
            ])

        def check_drug_unique():
            """Проверка уникальности названий ЛС."""
            df = pd.read_excel(self.import_path, sheet_name=self.DRUGS_SHEET)
            return df[self.DRUG_COLUMN].is_unique

        def check_side_effect_unique():
            """Проверка уникальности названий ПД."""
            df = pd.read_excel(self.import_path, sheet_name=self.SIDE_EFFECTS_SHEET)
            return df[self.EFFECT_COLUMN].is_unique

        def check_side_effect_unique_en():
            """Проверка уникальности названий ПД на англ."""
            df = pd.read_excel(self.import_path, sheet_name=self.SIDE_EFFECTS_SHEET)
            return df[self.EFFECT_COLUMN_EN].is_unique

        if check_sheets():
            logger.debug('Все нужные листы в наличии')
            if check_tables():
                logger.debug('Все нужные таблицы в наличии')
                return all([
                    check_drug_unique(),
                    check_side_effect_unique(),
                    check_side_effect_unique_en()
                ])
            else:
                return False
        return False

    def _load_drugs(self):
        """Загрузка ЛС."""
        df = pd.read_excel(self.import_path, sheet_name=self.DRUGS_SHEET)

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
        df = pd.read_excel(self.import_path,
                           sheet_name=self.SIDE_EFFECTS_SHEET)        
        try:
            logger.info('Загрузка побочных действий началась')
            for _, side_effect, side_effect_en, weight in list(
                df.itertuples(index=False, name=None)):
                SideEffect.objects.create(
                    se_name=side_effect.strip(),
                    se_name_en=side_effect_en.strip(),
                    weight=weight)
            logger.info(f'Загружено побочных действий: {SideEffect.objects.count()}')
        except Exception as error:
            raise Exception(f'Проблема с загрузкой {error}')

    def _load_ranks(self):
        """Загрузка рангов."""
        df = pd.read_excel(self.import_path, sheet_name=self.RANKS_SHEET)

        df = df.iloc[1:, 2:]
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
                self.NUMBER_COLUMN: numbers,
                self.DRUG_COLUMN: drug_names
            }
        )

    def _export_side_effects(self):
        """Экспорт ПД."""
        side_effects = SideEffect.objects.order_by('index')
        numbers = [side_effect.index for side_effect in side_effects]
        side_effect_names = [side_effect.se_name for side_effect in side_effects]
        side_effect_names_en = [side_effect.se_name_en for side_effect in side_effects]
        weights = [side_effect.weight for side_effect in side_effects]

        self.side_effects_df = pd.DataFrame(
            {
                self.NUMBER_COLUMN: numbers,
                'эффект': side_effect_names,
                'эффект (англ.)': side_effect_names_en,
                'ранг': weights
            }
        )

    def _export_rangs(self):
        """Экспорт рангов."""
        side_effects = SideEffect.objects.order_by('index')
        drugs = Drug.objects.order_by('index')
        column_headers = [side_effect.index for side_effect in side_effects]
        side_effect_names = [side_effect.se_name for side_effect in side_effects]

        rows = []
        rows.append(side_effect_names)

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

        with pd.ExcelWriter(self.export_path, engine='openpyxl') as writer:
            self.drugs_df.to_excel(writer,
                                   sheet_name=self.DRUGS_SHEET,
                                   index=False,
                                   startcol=0)
            self.side_effects_df.to_excel(writer,
                                          sheet_name=self.SIDE_EFFECTS_SHEET,
                                          index=False,
                                          startcol=0)

            self.drugs_df.columns = [''] * len(self.drugs_df.columns)
            new_row = pd.DataFrame([[None, self.DRUG_SIDE_EFFECT]], columns=self.drugs_df.columns)
            self.drugs_df = pd.concat([new_row, self.drugs_df], ignore_index=True)

            df_combined = pd.concat([self.drugs_df, df], ignore_index=False, axis=1)

            df_combined.to_excel(writer, sheet_name=self.RANKS_SHEET, index=False)

    def _add_export_date_sheet(self):
        """Добавляет отдельный лист с текущей датой экспорта."""
        from datetime import datetime

        now = datetime.now()
        df = pd.DataFrame(
            {
                'Дата экспорта данных о рангах из БД': [
                    now.strftime('%d.%m.%Y')],
                'Время экспорта данных о рангах из БД': [
                    now.strftime('%H:%M:%S')]
            }
        )

        with pd.ExcelWriter(self.export_path,
                            engine='openpyxl',
                            mode='a',
                            if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=self.EXPORT_DATE_SHEET, index=False)

    def export_from_db(self):
        """Экспорт из БД."""
        open(self.export_path, 'w', encoding='utf-8').close()
        super().export_from_db()
        self._add_export_date_sheet()
