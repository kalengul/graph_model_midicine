"""Модуль загрузки запрещённый пар ЛС."""

from abc import ABC, abstractmethod
import logging
import os

import pandas as pd

from drugs.models import BannedDrugPair
from drugs.utils.custom_exception import (PairFileError,
                                          PairDBError)
from drugs.utils.cleaner import BannedDrugPairCleanProcessor


logger = logging.getLogger('drugs')


class BannedPairLoader(ABC):
    """Абстрактный загрузчик запрещённых пар."""

    @abstractmethod
    def load_to_db(self):
        """Загрузка запрещённых пар."""

    @abstractmethod
    def clear_db(self):
        """Очистка БД от старых пар ЛС."""


class PandasBannedPairLoader(BannedPairLoader):
    """Загрузчик запрещённых пар с помощью pandas."""

    DRUG1 = 'drug1'
    DRUG2 = 'drug2' 

    def __init__(self, import_path):
        self.import_path = import_path

    @abstractmethod
    def load_to_db(self):
        """Загрузка запрещённых пар."""

    def clear_db(self):
        """Очистка БД от старых пар ЛС."""
        BannedDrugPairCleanProcessor().get_cleaner().clear_table()

class CSVBannedPairLoader(PandasBannedPairLoader):
    """Загрузчик запрещённых пар."""

    def load_to_db(self):
        """Загрузка запрещённых пар из CSV-файлов."""
        try:
            df = pd.read_csv(self.import_path, header=0, names=[self.DRUG1, self.DRUG2])
        except Exception as error:
            message = ('Проблема загрузки пар ЛС. '
                       f'Ошибка чтения csv-файла {os.path.basename(self.import_path)}')
            logger.error(message)
            raise PairFileError(message) from error

        df[self.DRUG1] = df[self.DRUG1].str.strip()
        df[self.DRUG2] = df[self.DRUG2].str.strip()
        df[self.DRUG1] = df[self.DRUG1].str.replace(r'\s*\+\s*', '+', regex=True)
        df[self.DRUG2] = df[self.DRUG2].str.replace(r'\s*\+\s*', '+', regex=True)
        df[self.DRUG1] = df[self.DRUG1].str.lower()
        df[self.DRUG2] = df[self.DRUG2].str.lower()

        seen_pairs = set()
        unique_rows = []

        try:
            for _, row in df.iterrows():
                drug1, drug2 = row[self.DRUG1], row[self.DRUG2]
                normal_pair = (drug1, drug2)
                reverse_pair = (drug2, drug1)

                if reverse_pair in seen_pairs or normal_pair in seen_pairs:
                    continue

                seen_pairs.add(normal_pair)
                unique_rows.append((drug1, drug2))

                BannedDrugPair.objects.create(first_drug=drug1, second_drug=drug2)
        except Exception as error:
            message = ('Проблема загрузки пар ЛС. '
                       'Ошибка при добавлении пары в БД')
            logger.error(message)
            raise PairFileError(message) from error

    def clear_db(self):
        """Очистка БД от старых пар ЛС."""
        super().clear_db()
