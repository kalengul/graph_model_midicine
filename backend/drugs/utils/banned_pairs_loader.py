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
from typing import List, Dict, Tuple

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


    def clear_db(self):
        """Очистка БД от старых пар ЛС."""
        BannedDrugPairCleanProcessor().get_cleaner().clear_table()


# class GroupBannedPairLoader (ABC):
#     """
#     Загрузчик запрещённых пар ЛС на основе групп из .json.
#     """

#     # Ключи полей 
#     DRUG_KEY = 'drug'
#     GROUP_KEY = 'group'
#     BANNED_GROUPS_KEY = 'banned_groups'

#     @staticmethod
#     def normalize_plus_sign(text: str) -> str:
#         """
#         Нормализует пробелы вокруг знака '+'.
#         Пример: "Препарат + Другой" -> "Препарат+Другой"
#         """
#         return re.sub(r'\s*\+\s*', '+', text)

#     @classmethod
#     def preprocess_drug_name(self, drug_name):
#         """
#         Предобработка названия препарата:
#         1. Удаление пробелов в начале и конце
#         2. Нормализация пробелов вокруг знака +
#         3. Приведение к нижнему регистру
#         """
#         if not drug_name:
#             return drug_name
            
#         # Удаляем пробелы в начале и конце
#         processed = drug_name.strip()
        
#         # Нормализуем пробелы вокруг знака +
#         processed = self.normalize_plus_sign(processed)
        
#         # Приводим к нижнему регистру для регистронезависимого сравнения
#         processed = processed.lower()
        
#         return processed

#     def find_banned_pairs_by_group(self, data: List[Dict]) -> List[Tuple[str, str]]:
#         """
#         Анализирует входные данные и возвращает список уникальных пар (drug1, drug2),
#         которые должны быть запрещены согласно логике групп.
#         """
#         # Индекс: группа -> множество препаратов
#         group_to_drugs: Dict[str, Set[str]] = {}

#         # Сначала заполняем индекс
#         for item in data:
#             drug = self.preprocess_drug_name(item.get(self.DRUG_KEY))
#             group = item.get(self.GROUP_KEY)
#             if drug and group:
#                 group_to_drugs.setdefault(group, set()).add(drug)

#         # Множество для хранения уникальных пар (отсортированных)
#         pairs: Set[Tuple[str, str]] = set()

#         # Проходим по данным и формируем пары
#         for item in data:
#             drug1 = self.preprocess_drug_name(item.get(self.DRUG_KEY))
#             banned_groups = item.get(self.BANNED_GROUPS_KEY, [])

#             for banned_group in banned_groups:
#                 for drug2 in group_to_drugs.get(banned_group, []):
#                     if drug1 == drug2:
#                         continue
#                     # Сортируем, чтобы пара была канонической (first_drug, second_drug)
#                     pair = tuple(sorted([drug1, drug2]))
#                     pairs.add(pair)

#         return list(pairs)

#     def load_to_db(self, *args, **kwargs):
#         """
#         Загружает запрещённые пары в БД.
#         Ожидает именованный аргумент 'data' со списком словарей.
#         Возвращает количество созданных записей.
#         """
#         data = kwargs.get('data')
#         if data is None:
#             raise ValueError("Не передан обязательный параметр 'data'")

#         # 1. Получаем все потенциальные пары по группам
#         new_pairs = self.find_banned_pairs_by_group(data)

#         # 2. Получаем уже существующие пары из БД в виде множества отсортированных кортежей
#         existing_pairs = set()
#         for first, second in BannedDrugPair.objects.values_list('first_drug', 'second_drug'):
#             # Приводим к нормализованному виду на случай, если в БД есть неканонические записи
#             norm_first = self.normalize_drug_name(first)
#             norm_second = self.normalize_drug_name(second)
#             existing_pairs.add(tuple(sorted([norm_first, norm_second])))

#         # 3. Оставляем только те, которых ещё нет
#         pairs_to_add = [pair for pair in new_pairs if pair not in existing_pairs]

#         # 4. Создаём записи в БД
#         created_count = 0
#         for first, second in pairs_to_add:
#             BannedDrugPair.objects.create(first_drug=first, second_drug=second)
#             created_count += 1
#             # Здесь можно добавить логирование, например:
#             # logger.debug(f"Создана пара: {first} – {second}")

#         # 5. Возвращаем результат (можно также вернуть список добавленных пар)
#         return created_count