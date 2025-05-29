"""Модуль выдуль не посредственного вычисления."""

import logging

import numpy as np

from drugs.models import Drug, SideEffect, DrugSideEffect


logger = logging.getLogger('fortran')


class FortranCalculator:
    """
    Вычислитель рангов для лекарств и побочных эффектов.
    """

    _DEFAULT_RANK_NAME = 'rang_base'

    @classmethod
    def get_default_rank_name(cls):
        return cls._DEFAULT_RANK_NAME

    def __init__(self):
        self.n_j = Drug.objects.count()
        self.n_k = SideEffect.objects.count()

    def calculate(self, rank_name, nj):
        logger.debug(f"Индексы входных ЛС (nj): {nj}")

        non_zero_nj = [idx for idx in nj if idx != 0]
        unique_nj = list(set(non_zero_nj))
        num_drugs = len(unique_nj)

        if rank_name is None:
            rank_name = self.get_default_rank_name()

        logger.debug(f"Используемый ранг: {rank_name}")

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

        logger.debug(f'len(side_effects) = {len(side_effects)}')

        # Анализ потенциальных ЛС
        rangs_matrix = np.array(rangs).reshape(self.n_j, self.n_k)
        unique_nj_sub_1 = [idx - 1 for idx in unique_nj]
        drugs_class_2, drugs_class_3 = [], []

        logger.debug(f'rangs_matrix = {rangs_matrix}')
        logger.debug(f'unique_nj_sub_1 = {unique_nj_sub_1}')
        for j in range(self.n_j):
            if j not in unique_nj_sub_1:
                new_rangsum = rangsum + rangs_matrix[j]
                max_rang = np.max(new_rangsum)
                logger.debug(f'j = {j}')
                logger.debug(f'max_rang = {max_rang}')
                if max_rang >= 1.0:
                    drugs_class_3.append(j)
                elif max_rang >= 0.5:
                    drugs_class_2.append(j)

        drug_array2 = [{'name': Drug.objects.get(index=j+1).drug_name, 'class': 2} for j in drugs_class_2]
        drug_array3 = [{'name': Drug.objects.get(index=j+1).drug_name, 'class': 3} for j in drugs_class_3]

        context['combinations'] = [
            {"сompatibility": 'cause', "drugs": [d['name'] for d in drug_array2]},
            {"сompatibility": 'incompatible', "drugs": [d['name'] for d in drug_array3]},
        ]

        context['drugs'] = [Drug.objects.get(index=i).drug_name for i in unique_nj]

        return context
