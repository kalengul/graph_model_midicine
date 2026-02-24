"""Модуль загрузки запрещённый пар ЛС."""

from abc import ABC, abstractmethod
import logging
import os
import re

import pandas as pd

from drugs.models import BannedDrugPair, Drug
from drugs.utils.custom_exception import (PairFileError,
                                          PairDBError)
from drugs.utils.cleaner import BannedDrugPairCleanProcessor


logger = logging.getLogger('drugs')


class BannedPairLoader(ABC):
    """Абстрактный загрузчик запрещённых пар."""

    @abstractmethod
    def load_to_db(self, *args, **kwargs):
        """Загрузка запрещённых пар."""

    @abstractmethod
    def clear_db(self):
        """Очистка БД от старых пар ЛС."""


class PandasBannedPairLoader(BannedPairLoader):
    """Загрузчик запрещённых пар с помощью pandas."""

    DRUG1 = 'drug1'
    DRUG2 = 'drug2'
    COMMENT = 'comment'
    DRUG1_NUMBER = 0
    DRUG2_NUMBER = 1
    COMMENT_NUMBER = 2
    NULL_VALUES = ['', 'nan', 'NaN', 'NAN', 'null',
                   'NULL', 'none', 'None', 'NONE', ' ']

    def __init__(self, import_path=None):
        """Инициализатор."""
        self.import_path = import_path

    @abstractmethod
    def load_to_db(self, *args, **kwargs):
        """Загрузка запрещённых пар."""

    def clear_db(self):
        """Очистка БД от старых пар ЛС."""
        BannedDrugPairCleanProcessor().get_cleaner().clear_table()


class CSVBannedPairLoader(PandasBannedPairLoader):
    """Загрузчик запрещённых пар."""

    def load_to_db(self, *args, **kwargs):
        """Загрузка запрещённых пар из CSV-файлов."""
        try:
            df = pd.read_csv(self.import_path,
                             na_values=self.NULL_VALUES,
                             keep_default_na=True,
                             sep=';')

            df = df.rename(
                columns={df.columns[self.DRUG1_NUMBER]: self.DRUG1,
                         df.columns[self.DRUG2_NUMBER]: self.DRUG2,
                         df.columns[self.COMMENT_NUMBER]: self.COMMENT})

            logger.debug(f'df.shape = {df.shape}')
        except Exception as error:
            message = (
                'Проблема загрузки пар ЛС. '
                'Ошибка чтения csv-файла'
                f' {os.path.basename(self.import_path)}')
            logger.error(message)
            raise PairFileError(message) from error

        df = df.dropna(subset=[self.DRUG1, self.DRUG2])

        df[self.DRUG1] = df[self.DRUG1].str.strip()
        df[self.DRUG2] = df[self.DRUG2].str.strip()
        df[self.DRUG1] = df[self.DRUG1].str.replace(r'\s*\+\s*',
                                                    '+',
                                                    regex=True)
        df[self.DRUG2] = df[self.DRUG2].str.replace(r'\s*\+\s*',
                                                    '+',
                                                    regex=True)
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

                comment = row[self.COMMENT]
                comment = (
                    None if pd.isna(comment)
                    else str(comment).strip().lower())
                print('comment =', comment)

                if (Drug.objects.filter(drug_name__iexact=drug1).exists()
                        and Drug.objects.filter(drug_name__iexact=drug2
                                                ).exists()):
                    logger.debug('Есть в БД')
                    logger.debug(f'drug1 = {drug1}')
                    logger.debug(f'drug2 = {drug2}')
                    BannedDrugPair.objects.create(first_drug=drug1,
                                                  second_drug=drug2,
                                                  comment=comment)
                else:
                    logger.debug('Нет в БД')
                    logger.debug(f'drug1 = {drug1}')
                    logger.debug(f'drug2 = {drug2}')
        except Exception as error:
            message = ('Проблема загрузки пар ЛС. '
                       'Ошибка при добавлении пары в БД')
            logger.error(message)
            raise PairDBError(message) from error

    def clear_db(self):
        """Очистка БД от старых пар ЛС."""
        super().clear_db()


class JSONBannedPairLoader(ABC):
    """Загрузчик запрещённых пар из JSON."""

    DRUG = "drug"
    BANNED_DRUGS = "banned_drugs"
    DATA = "data"

    @staticmethod
    def normalize_plus_sign(text):
        """
        Нормализует пробелы вокруг знака '+'.
        Пример: "Препарат + Другой" -> "Препарат+Другой"
        """
        # Заменяем пробелы вокруг + на просто +
        return re.sub(r'\s*\+\s*', '+', text)

    def preprocess_drug_name(self, drug_name):
        """
        Предобработка названия препарата:
        1. Удаление пробелов в начале и конце
        2. Нормализация пробелов вокруг знака +
        3. Приведение к нижнему регистру
        """
        if not drug_name:
            return drug_name
            
        # Удаляем пробелы в начале и конце
        processed = drug_name.strip()
        
        # Нормализуем пробелы вокруг знака +
        processed = self.normalize_plus_sign(processed)
        
        # Приводим к нижнему регистру для регистронезависимого сравнения
        processed = processed.lower()
        
        return processed

    def load_to_db(self, *args, **kwargs):
        """Загрузка запрещённых пар из JSON-файлов."""
        created_pairs = set()  # Множество для отслеживания созданных пар
        skipped_pairs = 0
        created_count = 0
        not_found_drugs = set()  # Для сбора отсутствующих препаратов
        
        try:
            drugs = kwargs[self.DATA]

            for drug in drugs:
                # Предобработка основного препарата
                raw_drug1 = drug[self.DRUG]
                drug1 = self.preprocess_drug_name(raw_drug1)
                
                if not drug1:
                    logger.debug(f'Пустое название препарата, пропускаем')
                    continue

                for raw_drug2 in drug[self.BANNED_DRUGS]:
                    # Предобработка запрещённого препарата
                    drug2 = self.preprocess_drug_name(raw_drug2)
                    
                    if not drug2:
                        logger.debug(f'Пустое название запрещённого препарата, пропускаем')
                        continue
                    
                    # Пропускаем, если препараты одинаковые
                    if drug1 == drug2:
                        logger.debug(f'Одинаковые препараты: {drug1} = {drug2}, пропускаем')
                        continue
                    
                    # Проверяем существование обоих препаратов в Drug (регистронезависимо)
                    # Используем предобработанные названия для поиска
                    drug1_obj = Drug.objects.filter(drug_name__iexact=drug1).first()
                    drug2_obj = Drug.objects.filter(drug_name__iexact=drug2).first()
                    
                    if drug1_obj and drug2_obj:
                        # Сортируем названия для единообразного хранения
                        first, second = sorted([drug1, drug2])
                        pair_key = f"{first}|{second}"  # Уникальный ключ пары
                        
                        # Проверяем, не создавали ли уже такую пару
                        if pair_key not in created_pairs:
                            # Проверяем, нет ли уже такой пары в БД (на случай, если clear_db не очистила)
                            if not BannedDrugPair.objects.filter(
                                first_drug__iexact=first, 
                                second_drug__iexact=second
                            ).exists():
                                BannedDrugPair.objects.create(
                                    first_drug=first,
                                    second_drug=second
                                )
                                created_pairs.add(pair_key)
                                created_count += 1
                                logger.debug(f'Создана пара: {first} - {second}')
                            else:
                                logger.debug(f'Пара уже существует в БД: {first} - {second}')
                        else:
                            logger.debug(f'Дубликат пары в файле: {first} - {second}, пропускаем')
                    else:
                        skipped_pairs += 1
                        if not drug1_obj:
                            not_found_drugs.add(f"'{raw_drug1}' (нормализовано: '{drug1}')")
                        if not drug2_obj:
                            not_found_drugs.add(f"'{raw_drug2}' (нормализовано: '{drug2}')")
                        
            # Логируем отсутствующие препараты одной группой
            if not_found_drugs:
                logger.warning(f'Препараты не найдены в БД: {", ".join(not_found_drugs)}')
                
            logger.info(f'Загрузка завершена. Создано пар: {created_count}, пропущено: {skipped_pairs}')
            
        except Exception as error:
            message = ('Проблема загрузки пар ЛС. '
                       'Ошибка при добавлении пары в БД')
            logger.error(message)
            raise PairDBError(message) from error


    def clear_db(self):
        """Очистка БД от старых пар ЛС."""
        BannedDrugPairCleanProcessor().get_cleaner().clear_table()
