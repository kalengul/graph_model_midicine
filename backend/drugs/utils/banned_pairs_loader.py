"""Модуль загрузки запрещённый пар ЛС."""

from abc import ABC, abstractmethod
import logging
import os
import re

import pandas as pd

from drugs.models import BannedDrugPair, Drug
from drugs.utils.custom_exception import (PairFileError,
                                          PairDBError)
# from drugs.utils.cleaner import BannedDrugPairCleanProcessor
from drugs.utils.universal_cleaner import universal_cleaner
from typing import List, Dict, Tuple

logger = logging.getLogger('drugs')


class BannedPairLoader(ABC):
    """Абстрактный загрузчик запрещённых пар."""

    @abstractmethod
    def load_to_db(self, *args, **kwargs):
        """Загрузка запрещённых пар."""

    # @abstractmethod
    def clear_db(self):
        """Очистка БД от старых пар ЛС."""
        universal_cleaner(model_classes=[BannedDrugPair]).clear_table()


class PandasBannedPairLoader(BannedPairLoader):
    """
    Универсальный загрузчик запрещённых пар из CSV (; разделитель) и Excel.
    Формат определяется по расширению файла.
    """

    DRUG1 = 'first_drug'
    DRUG2 = 'second_drug'
    COMMENT = 'comment'
    # DRUG1_NUMBER = 0
    # DRUG2_NUMBER = 1
    # COMMENT_NUMBER = 2
    NULL_VALUES = ['', 'nan', 'NaN', 'NAN', 'null',
                   'NULL', 'none', 'None', 'NONE', ' ']

    def __init__(self, import_path=None):
        """Инициализатор."""
        self.import_path = import_path

    def _read_file_to_dataframe(self):
        """Определяет формат файла и возвращает DataFrame."""
        ext = os.path.splitext(self.import_path)[1].lower()
        try:
            if ext == '.csv':
                df = pd.read_csv(
                    self.import_path,
                    na_values=self.NULL_VALUES,
                    keep_default_na=True,
                    sep=';'
                )
            elif ext in ('.xlsx', '.xls'):
                df = pd.read_excel(
                    self.import_path,
                    na_values=self.NULL_VALUES,
                    keep_default_na=True,
                    dtype=str   # читаем всё как строки для единой обработки
                )
            else:
                raise PairFileError(f'Неподдерживаемый формат: {ext}. Ожидается .csv, .xlsx или .xls')

            logger.debug(f'Файл прочитан, форма={df.shape}')
            return df
        except Exception as e:
            message = (
                f'Проблема загрузки пар ЛС. '
                f'Ошибка чтения файла {os.path.basename(self.import_path)}: {str(e)}'
            )
            logger.error(message)
            raise PairFileError(message) from e

    def load_to_db(self, *args, **kwargs):
        """Загрузка запрещённых пар из CSV или Excel."""
        df = self._read_file_to_dataframe()

        # --- Общая логика обработки (как в CSVBannedPairLoader) ---
        df = df.dropna(subset=[self.DRUG1, self.DRUG2])

        df[self.DRUG1] = df[self.DRUG1].astype(str).str.strip()
        df[self.DRUG2] = df[self.DRUG2].astype(str).str.strip()
        df[self.DRUG1] = df[self.DRUG1].str.replace(r'\s*\+\s*', '+', regex=True)
        df[self.DRUG2] = df[self.DRUG2].str.replace(r'\s*\+\s*', '+', regex=True)
        df[self.DRUG1] = df[self.DRUG1].str.lower()
        df[self.DRUG2] = df[self.DRUG2].str.lower()

        seen_pairs = set()

        stats = {
            'duplicates_skipped': 0,            # дубли внутри файла
            'drug_not_found': 0,                # нет одного из ЛС в справочнике
            'created': 0,                       # успешно создано
        }

        try:
            for _, row in df.iterrows():
                drug1, drug2 = row[self.DRUG1], row[self.DRUG2]
                normal_pair = (drug1, drug2)
                reverse_pair = (drug2, drug1)

                if reverse_pair in seen_pairs or normal_pair in seen_pairs:
                    stats['duplicates_skipped'] += 1
                    continue
                seen_pairs.add(normal_pair)

                comment = row.get(self.COMMENT)
                comment = None if pd.isna(comment) else str(comment).strip().lower()

                drug1_exists = Drug.objects.filter(drug_name__iexact=drug1).exists()
                drug2_exists = Drug.objects.filter(drug_name__iexact=drug2).exists()

                if drug1_exists and drug2_exists:
                    _, created = BannedDrugPair.objects.get_or_create(
                        first_drug=drug1,
                        second_drug=drug2,
                        defaults={'comment': comment}
                    )
                    if created:
                        stats['created'] += 1
                    else:
                        # пара уже существовала в БД (хотя обычно таблица чистится)
                        stats['duplicates_skipped'] += 1
                else:
                    stats['drug_not_found'] += 1
                    logger.debug(f'Нет в БД: {drug1}, {drug2}')

            # Логируем или возвращаем статистику
            logger.info(f'Статистика загрузки: {stats}')
            # Если нужно вернуть в ответе – сохранить stats в self или вернуть из метода
            return stats

        except Exception as e:
            message = 'Проблема загрузки пар ЛС. Ошибка при добавлении пары в БД'
            logger.error(message)
            raise PairDBError(message) from e

class JSONBannedPairLoader(ABC):
    """Загрузчик запрещённых пар из JSON."""

    DRUG = "drug"
    BANNED_DRUGS = "banned_drugs"
    DATA = "data"
    BANNED_GROUPS = "banned_groups"

    @staticmethod
    def _normalize_plus_sign(text):
        """
        Нормализует пробелы вокруг знака '+'.
        Пример: "Препарат + Другой" -> "Препарат+Другой"
        """
        # Заменяем пробелы вокруг + на просто +
        return re.sub(r'\s*\+\s*', '+', text)

    def _preprocess_drug_name(self, drug_name):
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
        processed = self._normalize_plus_sign(processed)
        
        # Приводим к нижнему регистру для регистронезависимого сравнения
        processed = processed.lower()
        
        return processed

    def _expand_by_groups(self, drugs_data):
        """
        Расширяет поле 'banned_drugs' для каждого препарата,
        добавляя нормализованные названия препаратов из групп, указанных в 'banned_groups'.
        Модифицирует список на месте.
        """
        # Индекс группа → множество нормализованных препаратов
        group_to_drugs = {}
        for item in drugs_data:
            drug = self._preprocess_drug_name(item.get(self.DRUG))
            groups = item.get('group', [])  # Теперь groups - это список
            
            if drug and groups:
                # Если groups - список, берем каждый элемент
                if isinstance(groups, list):
                    for group in groups:
                        if group:  # Проверяем что не пустое
                            group_to_drugs.setdefault(group, set()).add(drug)
                else:
                    # Если вдруг строка (для обратной совместимости)
                    group_to_drugs.setdefault(groups, set()).add(drug)

        # Для каждого препарата расширяем banned_drugs
        for item in drugs_data:
            drug1 = self._preprocess_drug_name(item.get(self.DRUG))
            banned_groups = item.get('banned_groups', [])
            
            if not banned_groups:
                continue
                
            additional = set()
            # banned_groups может быть списком
            if isinstance(banned_groups, list):
                for banned_group in banned_groups:
                    for drug2 in group_to_drugs.get(banned_group, []):
                        if drug1 != drug2:
                            additional.add(drug2)
            else:
                # Если строка
                for drug2 in group_to_drugs.get(banned_groups, []):
                    if drug1 != drug2:
                        additional.add(drug2)
                        
            if additional:
                current = set(item.get(self.BANNED_DRUGS, []))
                item[self.BANNED_DRUGS] = list(current | additional)
    
    def load_to_db(self, *args, **kwargs):
        """Загрузка запрещённых пар из JSON-файлов."""
        created_pairs = set()  # Множество для отслеживания созданных пар
        skipped_pairs = 0
        created_count = 0
        not_found_drugs = set()  # Для сбора отсутствующих препаратов
        
        try:
            drugs = kwargs[self.DATA]
            # --- НОВЫЙ ШАГ: группы ---
            self._expand_by_groups(drugs)
            for drug in drugs:
                # Предобработка основного препарата
                raw_drug1 = drug[self.DRUG]
                drug1 = self._preprocess_drug_name(raw_drug1)
                
                if not drug1:
                    logger.debug(f'Пустое название препарата, пропускаем')
                    continue

                for raw_drug2 in drug[self.BANNED_DRUGS]:
                    # Предобработка запрещённого препарата
                    drug2 = self._preprocess_drug_name(raw_drug2)
                    
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
                        drug_names = sorted([drug1, drug2])
                        first, second = drug_names[0], drug_names[1]
                        pair_key = f"{first}|{second}"
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
                                # logger.debug(f'Создана пара: {first} - {second}')
                            # else:
                                # logger.debug(f'Пара уже существует в БД: {first} - {second}')
                        # else:
                        #     logger.debug(f'Дубликат пары в файле: {first} - {second}, пропускаем')
                    else:
                        skipped_pairs += 1
                        if not drug1_obj:
                            not_found_drugs.add(f"'{raw_drug1}' (нормализовано: '{drug1}')")
                        if not drug2_obj:
                            not_found_drugs.add(f"'{raw_drug2}' (нормализовано: '{drug2}')")
                        
            # # Логируем отсутствующие препараты одной группой
            # if not_found_drugs:
            #     logger.warning(f'Препараты не найдены в БД: {", ".join(not_found_drugs)}')
                
            logger.info(f'Загрузка завершена. Создано пар: {created_count}, пропущено: {skipped_pairs}')
            
        except Exception as error:
            message = ('Проблема загрузки пар ЛС. '
                       'Ошибка при добавлении пары в БД')
            logger.error(message)
            raise PairDBError(message) from error


    # def clear_db(self):
    #     """Очистка БД от старых пар ЛС."""
    #     universal_cleaner(model_classes=[BannedDrugPair]).clear_table()
        # BannedDrugPairCleanProcessor().get_cleaner().clear_table()