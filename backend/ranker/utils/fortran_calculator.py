"""Модуль не посредственного вычисления."""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
import json
import numpy as np

from drugs.models import Drug, SideEffect, DrugSideEffect


logger = logging.getLogger('fortran')


class BaseCalculator(ABC):
    """Абстрактный базовый класс для вычислителей рангов."""

    _DEFAULT_RANK_NAME = 'rang_base'

    @classmethod
    def get_default_rank_name(cls):
        """Назначение ранга типа ранга по умолчанию."""
        return cls._DEFAULT_RANK_NAME

    @abstractmethod
    def __init__(self):
        """Инициализация вычислителя."""

    @abstractmethod
    def calculate(self, rank_name, nj):
        """Вычисление рангов."""


class FortranCalculator(BaseCalculator):
    """Вычислитель рангов для лекарств и побочных эффектов."""

    def __init__(self):
        """Инициализатор."""
        self.n_j = Drug.objects.count()
        self.n_k = SideEffect.objects.count()
        logger.debug(
            f"Инициализирован оригинальный калькулятор: {self.n_j} ЛС, "
            f"{self.n_k} ПЭ")

    def calculate(self, rank_name, nj):
        """Вычисление рангов."""
        # logger.debug(f"Индексы входных ЛС (nj): {nj}")

        non_zero_nj = [idx for idx in nj if idx != 0]
        unique_nj = list(set(non_zero_nj))
        num_drugs = len(unique_nj)

        if rank_name is None:
            rank_name = self.get_default_rank_name()

        # logger.debug(f"Используемый ранг: {rank_name}")

        # Создаем матрицу рангов для выбранных ЛС
        rangs = [getattr(r, rank_name) for r in DrugSideEffect.objects.all()]
        rang1 = np.zeros((num_drugs, self.n_k))

        for j, drug_idx in enumerate(unique_nj):
            for k in range(self.n_k):
                rang1[j, k] = rangs[self.n_k * (drug_idx - 1) + k]

        # Вычисление суммы рангов по эффектам
        rangsum = np.sum(rang1, axis=0)
        ram = np.max(rangsum)

        # Классификация
        if ram >= 1.0:
            classification = 'incompatible'
        elif ram >= 0.5:
            classification = 'caution'
        else:
            classification = 'compatible'

        context = {
            'rank_iteractions': round(float(ram), 2),
            'сompatibility_fortran': classification
        }

        # Распределение эффектов по классам
        side_effects = []
        for k in range(self.n_k):
            rank_val = rangsum[k]
            if rank_val >= 1.0:
                cls = 3
            elif rank_val >= 0.5:
                cls = 2
            else:
                cls = 1
            effect = SideEffect.objects.get(index=k+1)
            side_effects.append({
                'se_name': effect.se_name,
                'class': cls,
                'rank': round(float(rank_val), 2)
            })

        context['side_effects'] = [
            {"сompatibility": "compatible", 'effects': []},
            {"сompatibility": "caution", 'effects': []},
            {"сompatibility": "incompatible", 'effects': []},
        ]

        side_effects.sort(key=lambda x: x['rank'], reverse=True)
        for effect in side_effects:
            cls = effect.pop('class')
            context['side_effects'][cls - 1]['effects'].append(effect)

        # logger.debug(f'len(side_effects) = {len(side_effects)}')

        # Анализ потенциальных ЛС
        rangs_matrix = np.array(rangs).reshape(self.n_j, self.n_k)

        unique_nj_sub_1 = [idx - 1 for idx in unique_nj]
        drugs_class_2, drugs_class_3 = [], []
        # print('rangs_matrix.shape =', rangs_matrix.shape)
        # logger.debug(f'rangs_matrix = {rangs_matrix}')
        # logger.debug(f'unique_nj_sub_1 = {unique_nj_sub_1}')
        for j in range(self.n_j):
            # if j not in unique_nj_sub_1:
            new_rangsum = rangsum + rangs_matrix[j]
            max_rang = np.max(new_rangsum)
            logger.debug(f'j = {j}')
            logger.debug(f'max_rang = {max_rang}')
            if max_rang >= 1.0:
                drugs_class_3.append(j)
            elif max_rang >= 0.5:
                drugs_class_2.append(j)

        # print('drugs_class_3 =', drugs_class_3)
        # print('drugs_class_2 =', drugs_class_2)

        drug_array2 = [{'name': Drug.objects.get(index=j+1).drug_name,
                        'class': 2}
                       for j in drugs_class_2]

        # for j in drugs_class_3:
        #     print('Drug.objects.get(index=j+1).drug_name =',
        #           Drug.objects.get(index=j+1).drug_name)

        drug_array3 = [{'name': Drug.objects.get(index=j+1).drug_name,
                        'class': 3} 
                       for j in drugs_class_3]

        # print('drug_array3 =', drug_array3)

        context['combinations'] = [
            {"сompatibility": 'cause', "drugs": [d['name']
                                                 for d in drug_array2]},
            {"сompatibility": 'incompatible', "drugs": [d['name']
                                                        for d in drug_array3]},
        ]

        context['drugs'] = [Drug.objects.get(index=i).drug_name
                            for i in unique_nj]
        context["SEFromDrug"] = []
        for drug in [Drug.objects.get(index=i) for i in unique_nj]:
            # Получаем все связи DrugSideEffect для данного лекарства
            drug_side_effects = DrugSideEffect.objects.filter(drug=drug).select_related('side_effect')

            effects_data = []
            for dse in drug_side_effects:
                effects_data.append({
                    'se_name': dse.side_effect.se_name,
                    'rank': dse.rang_base  # или другой нужный ранг в зависимости от rank_name
                })

            context["SEFromDrug"].append(
                {
                    'd_name': drug.drug_name,
                    'effects': effects_data
                }
            )

        return context


class FortranCalculatorNormalization(BaseCalculator):
    """Вычислитель рангов для лекарств и побочных эффектов."""

    def __init__(self, canceling_effects_json=None):
        """Инициализатор."""
        self.n_j = Drug.objects.count()
        self.n_k = SideEffect.objects.count()
        logger.debug(
            f"Инициализирован калькулятор с нормализацией: {self.n_j} ЛС, "
            f"{self.n_k} ПЭ")

    def _apply_canceling_normalization(self, rangsum, canceling_groups):
        normalized_rangsum = rangsum.copy()
        #logger.debug(f'normalized_rangsum = {normalized_rangsum}')
        for group in canceling_groups:
            # Преобразуем индексы эффектов (1-based) в индексы массива (0-based)
            array_indices = [idx - 1 for idx in group]
            # Получаем ранги для эффектов в группе
            group_ranks = rangsum[array_indices]

            # Вычисляем общую сумму рангов в группе
            total_group_rank = np.sum(group_ranks)
            
            if total_group_rank == 0:
                continue

            # Вычисляем веса для каждого эффекта в группе
            weights = group_ranks / total_group_rank

            # Распределяем общую сумму пропорционально исходным рангам
            normalized_rangsum[array_indices]=group_ranks*weights

            #logger.debug(f'group_ranks = {group_ranks}, total_group_rank = {total_group_rank}, weights = {weights}, normalized_rangsum = {normalized_rangsum}')
        #logger.debug(f'normalized_rangsum = {normalized_rangsum}')
        return normalized_rangsum

    def calculate(self, rank_name, nj, canceling_groups=None):
        #canceling_groups: массив массивов индексов эффектов, которые нивелируют друг друга Формат: [[1, 2], [4, 5], [7, 10]]
        # Валидация входного массива
        logger.debug(f"Групп нивелирования: {canceling_groups}")
        if canceling_groups is not None:
            if not isinstance(canceling_groups, list):
                logger.error("cancel_groups должен быть списком")
                canceling_groups = None
            else:
                # Фильтруем только валидные группы
                valid_groups = []
                for group in canceling_groups:
                    if isinstance(group, list) and len(group) >= 2:
                        # Проверяем, что все индексы в допустимом диапазоне
                        valid_indices = [idx for idx in group if isinstance(idx, int) and 1 <= idx <= self.n_k]
                        if len(valid_indices) >= 2:
                            valid_groups.append(valid_indices)
                canceling_groups = valid_groups

        logger.debug(f"Групп нивелирования: {len(canceling_groups) if canceling_groups else 0}")

        non_zero_nj = [idx for idx in nj if idx != 0]
        unique_nj = list(set(non_zero_nj))
        num_drugs = len(unique_nj)


        if rank_name is None:
            rank_name = self.get_default_rank_name()

        # Создаем матрицу рангов для выбранных ЛС
        rangs = [getattr(r, rank_name) for r in DrugSideEffect.objects.all()]
        rang1 = np.zeros((num_drugs, self.n_k))

        for j, drug_idx in enumerate(unique_nj):
            for k in range(self.n_k):
                rang1[j, k] = rangs[self.n_k * (drug_idx - 1) + k]

        # Вычисление суммы рангов по эффектам
        rangsum = np.sum(rang1, axis=0)
        for k in range(self.n_k):
            logger.debug(f'k = {k}, rangsum[k] = {rangsum[k]}')
        # Применяем нормализацию для нивелирующих эффектов
        if canceling_groups:
            rangsum = self._apply_canceling_normalization(rangsum, canceling_groups)
        
        for k in range(self.n_k):
            logger.debug(f'k = {k}, rangsum[k] = {rangsum[k]}')
       
        ram = np.max(rangsum)

        # Классификация
        if ram >= 1.0:
            classification = 'incompatible'
        elif ram >= 0.5:
            classification = 'caution'
        else:
            classification = 'compatible'

        context = {
            'rank_iteractions': round(float(ram), 2),
            'сompatibility_fortran': classification
        }

        # Распределение эффектов по классам
        side_effects = []
        for k in range(self.n_k):
            rank_val = rangsum[k]
            if rank_val >= 1.0:
                cls = 3
            elif rank_val >= 0.5:
                cls = 2
            else:
                cls = 1
            effect = SideEffect.objects.get(index=k + 1)
            side_effects.append({
                'se_name': effect.se_name,
                'class': cls,
                'rank': round(float(rank_val), 2)
            })

        context['side_effects'] = [
            {"сompatibility": "compatible", 'effects': []},
            {"сompatibility": "caution", 'effects': []},
            {"сompatibility": "incompatible", 'effects': []},
        ]

        side_effects.sort(key=lambda x: x['rank'], reverse=True)
        for effect in side_effects:
            cls = effect.pop('class')
            context['side_effects'][cls - 1]['effects'].append(effect)

        # Анализ потенциальных ЛС
        rangs_matrix = np.array(rangs).reshape(self.n_j, self.n_k)

        unique_nj_sub_1 = [idx - 1 for idx in unique_nj]
        drugs_class_2, drugs_class_3 = [], []

        for j in range(self.n_j):
            new_rangsum = rangsum + rangs_matrix[j]
            # Применяем нормализацию для потенциальных комбинаций
            if canceling_groups:
                new_rangsum = self._apply_canceling_normalization(new_rangsum, canceling_groups)
            max_rang = np.max(new_rangsum)
            logger.debug(f'j = {j}, max_rang = {max_rang}')
            if max_rang >= 1.0:
                drugs_class_3.append(j)
            elif max_rang >= 0.5:
                drugs_class_2.append(j)

        drug_array2 = [{'name': Drug.objects.get(index=j + 1).drug_name,
                        'class': 2}
                       for j in drugs_class_2]

        drug_array3 = [{'name': Drug.objects.get(index=j + 1).drug_name,
                        'class': 3}
                       for j in drugs_class_3]

        context['combinations'] = [
            {"сompatibility": 'cause', "drugs": [d['name']
                                                 for d in drug_array2]},
            {"сompatibility": 'incompatible', "drugs": [d['name']
                                                        for d in drug_array3]},
        ]

        context['drugs'] = [Drug.objects.get(index=i).drug_name
                            for i in unique_nj]
        context["SEFromDrug"] = []
        for drug in [Drug.objects.get(index=i) for i in unique_nj]:
            # Получаем все связи DrugSideEffect для данного лекарства
            drug_side_effects = DrugSideEffect.objects.filter(drug=drug).select_related('side_effect')

            effects_data = []
            for dse in drug_side_effects:
                effects_data.append({
                    'se_name': dse.side_effect.se_name,
                    'rank': dse.rang_base  # или другой нужный ранг в зависимости от rank_name
                })

            context["SEFromDrug"].append(
                {
                    'd_name': drug.drug_name,
                    'effects': effects_data
                }
            )
        return context

class CalculatorMP(BaseCalculator):
    """Оптимизированная реализация для многопроцессорности."""

    def __init__(self):
        """Инициализация калькулятора рангов для многопроцессности."""
        logger.debug("Загрузка данных для CalculatorMP")

        self.drugs = list(Drug.objects.order_by('index'))
        self.n_j = len(self.drugs)
        self.drug_names = {drug.index: drug.drug_name for drug in self.drugs}
        self.drug_pk_to_index = {drug.pk: drug.index for drug in self.drugs}
        self.drug_name_to_index = {drug.drug_name: drug.index
                                   for drug in self.drugs}

        self.side_effects = list(SideEffect.objects.order_by('index'))
        self.n_k = len(self.side_effects)
        self.se_names = {se.index: se.se_name for se in self.side_effects}

        drug_side_effects = list(
            DrugSideEffect.objects.select_related('drug', 'side_effect')
            .order_by('drug__index', 'side_effect__index')
        )

        # Определение доступных типов рангов
        sample = drug_side_effects[0] if drug_side_effects else None
        self.available_ranks = [
            attr for attr in dir(sample)
            if attr.startswith('rang_') and not attr.startswith('_')
        ] if sample else [self._DEFAULT_RANK_NAME]

        # Построение матриц рангов для каждого типа ранга
        self.ranks_matrices = {}
        for rank_name in self.available_ranks:
            matrix = np.zeros((self.n_j, self.n_k), dtype=np.float32)
            for r in drug_side_effects:
                drug_idx = r.drug.index - 1
                se_idx = r.side_effect.index - 1
                matrix[drug_idx, se_idx] = float(getattr(r, rank_name, 0.0))
            self.ranks_matrices[rank_name] = matrix

        # Кэш побочных эффектов для каждого лекарства
        self.drug_side_effects_cache = defaultdict(list)
        for r in drug_side_effects:
            self.drug_side_effects_cache[r.drug.index].append({
                'se_name': r.side_effect.se_name,
                'rank': float(getattr(r, self._DEFAULT_RANK_NAME, 0.0))
            })

        logger.debug(
            f'CalculatorMP готов: {self.n_j} ЛС, {self.n_k} ПЭ, '
            f'ранги: {self.available_ranks}'
        )

    def calculate(self, rank_name=None, nj=None):
        """Вычисление БЕЗ обращений к БД — только работа с памятью."""
        if nj is None:
            nj = []
        if rank_name is None or rank_name not in self.ranks_matrices:
            rank_name = self._DEFAULT_RANK_NAME

        non_zero_nj = [self.drug_pk_to_index[pk] for pk in nj if pk != 0]
        unique_nj = list(set(non_zero_nj))
        num_drugs = len(unique_nj)

        if num_drugs == 0:
            return self._empty_result()

        matrix = self.ranks_matrices[rank_name]
        drug_indices_0based = [idx - 1 for idx in unique_nj]
        rang1 = matrix[drug_indices_0based, :]
        rangsum = np.sum(rang1, axis=0)
        ram = float(np.max(rangsum))

        # Классификация
        if ram >= 1.0:
            classification = 'incompatible'
        elif ram >= 0.5:
            classification = 'caution'
        else:
            classification = 'compatible'

        context = {
            'rank_iteractions': round(ram, 2),
            'сompatibility_fortran': classification
        }

        # Распределение побочных эффектов по классам
        side_effects = []
        for k in range(self.n_k):
            rank_val = float(rangsum[k])
            if rank_val >= 1.0:
                cls = 3
            elif rank_val >= 0.5:
                cls = 2
            else:
                cls = 1
            side_effects.append({
                'se_name': self.se_names[k + 1],
                'class': cls,
                'rank': round(rank_val, 2)
            })

        context['side_effects'] = [
            {"сompatibility": "compatible", 'effects': []},
            {"сompatibility": "caution", 'effects': []},
            {"сompatibility": "incompatible", 'effects': []},
        ]

        side_effects.sort(key=lambda x: x['rank'], reverse=True)
        for effect in side_effects:
            cls = effect.pop('class')
            context['side_effects'][cls - 1]['effects'].append(effect)

        # Анализ потенциальных лекарств
        drugs_class_2, drugs_class_3 = [], []

        for j in range(self.n_j):
            if (j + 1) not in unique_nj:
                new_rangsum = rangsum + matrix[j]
                max_rang = float(np.max(new_rangsum))
                if max_rang >= 1.0:
                    drugs_class_3.append(j)
                elif max_rang >= 0.5:
                    drugs_class_2.append(j)

        drug_array2 = [{'name': self.drug_names[j + 1], 'class': 2}
                       for j in drugs_class_2]
        drug_array3 = [{'name': self.drug_names[j + 1], 'class': 3}
                       for j in drugs_class_3]  # ИСПРАВЛЕНО

        context['combinations'] = [
            {"сompatibility": 'cause', "drugs": [d['name']
                                                 for d in drug_array2]},
            {"сompatibility": 'incompatible', "drugs": [d['name']
                                                        for d in drug_array3]},
        ]

        # Информация о лекарствах и их побочных эффектах
        context['drugs'] = [self.drug_names[i] for i in unique_nj]
        context["SEFromDrug"] = [
            {
                'd_name': self.drug_names[i],
                'effects': self.drug_side_effects_cache[i]
            } for i in unique_nj
        ]

        return context

    def _empty_result(self):
        """Результат для пустой комбинации."""
        return {
            'rank_iteractions': 0.0,
            'сompatibility_fortran': 'compatible',
            'side_effects': [
                {"сompatibility": "compatible", 'effects': []},
                {"сompatibility": "caution", 'effects': []},
                {"сompatibility": "incompatible", 'effects': []},
            ],
            'combinations': [
                {"сompatibility": 'cause', "drugs": []},
                {"сompatibility": 'incompatible', "drugs": []},
            ],
            'drugs': [],
            'SEFromDrug': []
        }


def get_calculator(use_multiprocessing=False, use_normalization=True):
    """
    Фабрика калькуляторов.

    Аргументы:
        use_multiprocessing (bool): True — использовать оптимизированную версию

    Возвращает:
        Экземпляр калькулятора
    """
    if use_multiprocessing:
        pass
        #return CalculatorMP()
    elif use_normalization:
        canceling_effects_json_manual=[[2,3],[5,14],[32,33],[51,52],[86,87]]
        #return FortranCalculatorNormalization(canceling_effects_json=canceling_effects_json_manual)
    else:
        pass
        #return FortranCalculator()
