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
    def calculate(self, rank_name, n_drug):
        """Вычисление рангов."""


class FortranCalculator(BaseCalculator):
    """Вычислитель рангов для лекарств и побочных эффектов."""

    def __init__(self):
        """Инициализатор."""
        self.n_drug = Drug.objects.count()
        self.n_side_effect = SideEffect.objects.count()
        logger.debug(
            f"Инициализирован оригинальный калькулятор: {self.n_drug} ЛС, "
            f"{self.n_side_effect} ПЭ")

    def calculate(self, rank_name, n_drug):
        """Вычисление рангов."""
        # logger.debug(f"Индексы входных ЛС (n_drug): {n_drug}")

        non_zero_n_drug = [idx for idx in n_drug if idx != 0]
        unique_n_drug = list(set(non_zero_n_drug))
        num_drugs = len(unique_n_drug)

        if rank_name is None:
            rank_name = self.get_default_rank_name()

        # logger.debug(f"Используемый ранг: {rank_name}")

        # Создаем матрицу рангов для выбранных ЛС
        rangs = [getattr(r, rank_name) for r in DrugSideEffect.objects.all()]
        rang1 = np.zeros((num_drugs, self.n_side_effect))

        for j, drug_idx in enumerate(unique_n_drug):
            for k in range(self.n_side_effect):
                rang1[j, k] = rangs[self.n_side_effect * (drug_idx - 1) + k]

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
            'compatibility_fortran': classification
        }

        # Распределение эффектов по классам
        side_effects = []
        for k in range(self.n_side_effect):
            rank_val = rangsum[k]
            if rank_val >= 1.0:
                cls = 3
            elif rank_val >= 0.5:
                cls = 2
            else:
                cls = 1
            effect = SideEffect.objects.get(id=k+1)
            side_effects.append({
                'se_name': effect.se_name,
                'class': cls,
                'rank': round(float(rank_val), 2)
            })

        context['side_effects'] = [
            {"compatibility": "compatible", 'effects': []},
            {"compatibility": "caution", 'effects': []},
            {"compatibility": "incompatible", 'effects': []},
        ]

        side_effects.sort(key=lambda x: x['rank'], reverse=True)
        for effect in side_effects:
            cls = effect.pop('class')
            context['side_effects'][cls - 1]['effects'].append(effect)

        # logger.debug(f'len(side_effects) = {len(side_effects)}')

        # Анализ потенциальных ЛС
        rangs_matrix = np.array(rangs).reshape(self.n_drug, self.n_side_effect)

        unique_n_drug_sub_1 = [idx - 1 for idx in unique_n_drug]
        drugs_class_2, drugs_class_3 = [], []
        print('rangs_matrix.shape =', rangs_matrix.shape)
        # logger.debug(f'rangs_matrix = {rangs_matrix}')
        # logger.debug(f'unique_n_drug_sub_1 = {unique_n_drug_sub_1}')
        for j in range(self.n_drug):
            if j not in unique_n_drug_sub_1:
                new_rangsum = rangsum + rangs_matrix[j]
                
                logger.debug(f'j = {j}')
                logger.debug(f'new_rangsum = {new_rangsum}')
                
                # Находим все побочные эффекты с value >= 1.0 для class 3
                print(f'np.where(new_rangsum >= 1.0)[0] = {np.where(new_rangsum >= 1.0)[0]}')
                indices_class_3 = np.where(new_rangsum >= 1.0)[0]
                if len(indices_class_3) > 0:
                    side_effects_class_3 = [{
                        'name': SideEffect.objects.get(id=idx+1).se_name,
                        'value': float(new_rangsum[idx])
                    } for idx in indices_class_3]
                    drugs_class_3.append({
                        'drug_index': j,
                        'side_effects': side_effects_class_3
                    })
                
                # Находим все побочные эффекты с 0.5 <= value < 1.0 для class 2
                indices_class_2 = np.where((new_rangsum >= 0.5) & (new_rangsum < 1.0))[0]
                if len(indices_class_2) > 0:
                    side_effects_class_2 = [{
                        'name': SideEffect.objects.get(id=idx+1).se_name,
                        'value': float(new_rangsum[idx])
                    } for idx in indices_class_2]
                    drugs_class_2.append({
                        'drug_index': j,
                        'side_effects': side_effects_class_2
                    })

        # print('drugs_class_3 =', drugs_class_3)
        # print('drugs_class_2 =', drugs_class_2)

        drug_array2 = [{
            'name': Drug.objects.get(id=item['drug_index']+1).drug_name,
            'class': 2,
            'side_effects': item['side_effects']
        } for item in drugs_class_2]

        # for item in drugs_class_3:
        #     print('Drug.objects.get(id=item["drug_index"]+1).drug_name =',
        #           Drug.objects.get(id=item['drug_index']+1).drug_name)

        drug_array3 = [{
            'name': Drug.objects.get(id=item['drug_index']+1).drug_name,
            'class': 3,
            'side_effects': item['side_effects']
        } for item in drugs_class_3]

        # print('drug_array3 =', drug_array3)

        context['combinations'] = [
            {
                "compatibility": 'caution', 
                "drugs": [{
                    "name": d['name'],
                    "side_effects": d['side_effects']
                } for d in drug_array2]
            },
            {
                "compatibility": 'incompatible', 
                "drugs": [{
                    "name": d['name'],
                    "side_effects": d['side_effects']
                } for d in drug_array3]
            },
        ]


        # Расчёт введённых препаратов по отдельности
        context['drugs'] = [Drug.objects.get(id=i).drug_name
                            for i in unique_n_drug]
        context["SEFromDrug"] = []
        for drug in [Drug.objects.get(id=i) for i in unique_n_drug]:
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
        self.n_drug = Drug.objects.count()
        self.n_side_effect = SideEffect.objects.count()
        logger.debug(
            f"Инициализирован калькулятор с нормализацией: {self.n_drug} ЛС, "
            f"{self.n_side_effect} ПЭ")

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

    def calculate(self, rank_name, n_drug, canceling_groups=None):
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
                        valid_indices = [idx for idx in group if isinstance(idx, int) and 1 <= idx <= self.n_side_effect]
                        if len(valid_indices) >= 2:
                            valid_groups.append(valid_indices)
                canceling_groups = valid_groups

        logger.debug(f"Групп нивелирования: {len(canceling_groups) if canceling_groups else 0}")

        non_zero_n_drug = [idx for idx in n_drug if idx != 0]
        unique_n_drug = list(set(non_zero_n_drug))
        num_drugs = len(unique_n_drug)

        if rank_name is None:
            rank_name = self.get_default_rank_name()

        # мапа побочных эффектов по индексам
        id2side_e = {
            k: SideEffect.objects.get(id=k+1).se_name
            for k in range(self.n_side_effect)
        }
        side_e2id = {v: k for k, v in id2side_e.items()}

        # Создаем матрицу рангов для выбранных ЛС
        rangs = [getattr(r, rank_name) for r in DrugSideEffect.objects.all()]
        rang1 = np.zeros((num_drugs, self.n_side_effect))

        for j, drug_idx in enumerate(unique_n_drug):
            for k in range(self.n_side_effect):
                rang1[j, k] = rangs[self.n_side_effect * (drug_idx - 1) + k]

        # Вычисление суммы рангов по эффектам
        rangsum = np.sum(rang1, axis=0)

        # Применяем нормализацию для нивелирующих эффектов
        if canceling_groups:
            rangsum = self._apply_canceling_normalization(rangsum, canceling_groups)
               
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
            'compatibility_fortran': classification
        }

        # Распределение эффектов по классам
        side_effects = []
        for k in range(self.n_side_effect):
            rank_val = rangsum[k]
            if rank_val >= 1.0:
                cls = 3
            elif rank_val >= 0.5:
                cls = 2
            else:
                cls = 1
            # effect = SideEffect.objects.get(id=k + 1)
            side_effects.append({
                # 'se_name': effect.se_name,
                'se_name': id2side_e[k],
                'class': cls,
                'rank': round(float(rank_val), 2)
            })

        context['side_effects'] = [
            {"compatibility": "compatible", 'effects': []},
            {"compatibility": "caution", 'effects': []},
            {"compatibility": "incompatible", 'effects': []},
        ]

        side_effects.sort(key=lambda x: x['rank'], reverse=True)
        for effect in side_effects:
            cls = effect.pop('class')
            context['side_effects'][cls - 1]['effects'].append(effect)

        # Анализ потенциальных ЛС

        # Составление словаря групп
        # Получаем ID всех групп, к которым относятся выбранные препараты
        drugs_with_groups = Drug.objects.filter(id__in=unique_n_drug).prefetch_related('drug_groups')
        group_ids = set()
        for drug in drugs_with_groups:
            for group in drug.drug_groups.all():
                group_ids.add(group.id)

        # 3. Получаем ID всех препаратов из этих групп (исключая выбранные)
        excluded_drug_ids = set(
            Drug.objects.filter(drug_groups__id__in=group_ids)
            .exclude(id__in=unique_n_drug)
            .values_list('id', flat=True)
            .distinct()
        )
        # Переводим в 0-индексацию
        excluded_drug_ids = {drug_id - 1 for drug_id in excluded_drug_ids}
        logger.debug(f"Исключаемые индексы препаратов: {sorted(excluded_drug_ids)}")

        rangs_matrix = np.array(rangs).reshape(self.n_drug, self.n_side_effect)
        drugs_class_2, drugs_class_3 = [], []
        unique_n_drug_sub_1 = [idx - 1 for idx in unique_n_drug]

        for j in range(self.n_drug):
            # Пропускаем выбранные и исключенные препараты
            if j in unique_n_drug_sub_1 or j in excluded_drug_ids:
                continue

            new_rangsum = rangsum + rangs_matrix[j]

            # Применяем нормализацию для потенциальных комбинаций
            if canceling_groups:
                new_rangsum = self._apply_canceling_normalization(new_rangsum, canceling_groups)

            # Находим все побочные эффекты с value >= 1.0 для class 3
            indices_class_3 = np.where(new_rangsum >= 1.0)[0]
            if len(indices_class_3) > 0:
                side_effects_class_3 = [{
                    'se_name': SideEffect.objects.get(id=idx+1).se_name,
                    'rank': round(float(new_rangsum[idx]), 2)
                } for idx in indices_class_3]
                drugs_class_3.append({
                    'drug_index': j,
                    'side_effects': side_effects_class_3
                })
            
            # Находим все побочные эффекты с 0.5 <= value < 1.0 для class 2
            indices_class_2 = np.where((new_rangsum >= 0.5) & (new_rangsum < 1.0))[0]
            if len(indices_class_2) > 0:
                side_effects_class_2 = [{
                    'se_name': SideEffect.objects.get(id=idx+1).se_name,
                    'rank': round(float(new_rangsum[idx]),2)
                } for idx in indices_class_2]
                drugs_class_2.append({
                    'drug_index': j,
                    # 'side_effects': side_effects_class_2
                    'side_effects': []
                })

        drug_array2 = [{
            'name': Drug.objects.get(id=item['drug_index']+1).drug_name,
            'class': 2,
            'side_effects': item['side_effects']
        } for item in drugs_class_2]

        drug_array3 = [{
            'name': Drug.objects.get(id=item['drug_index']+1).drug_name,
            'class': 3,
            'side_effects': item['side_effects']
        } for item in drugs_class_3]

        context['combinations'] = [
            {
                "compatibility": 'caution', 
                "drugs": [{
                    "name": d['name'],
                    "side_effects": d['side_effects']
                } for d in drug_array2]
            },
            {
                "compatibility": 'incompatible', 
                "drugs": [{
                    "name": d['name'],
                    "side_effects": d['side_effects']
                } for d in drug_array3]
            },
        ]


        context['drugs'] = [Drug.objects.get(id=i).drug_name
                            for i in unique_n_drug]
        

        # Если комбинация несовместима, нужны рекомендации
        if context["compatibility_fortran"] == "incompatible":
            context['rep_recommendations'] = self.analyze_max_drug_contribution(context['side_effects'][2]['effects'], rangs, unique_n_drug, rangsum, side_e2id)
            # context['rep_recommendations'] = [
            #     {
            #     "group_name": "Название группы1",
            #     "drugs": [
            #         {
            #             "drug_name": "Препарат1",
            #             "replace_drugs": ["Препарат2", "Препарат3"]
            #         },
            #         {
            #             "drug_name": "Препарат4",
            #             "replace_drugs": ["Препарат5", "Препарат6"]
            #         }
            #     ]
            #     },
            #     {
            #     "group_name": "Название группы2",
            #     "drugs": [
            #         {
            #             "drug_name": "Препарат4",
            #             "replace_drugs": ["Препарат5", "Препарат6"]
            #         },
            #         {
            #             "drug_name": "Препарат1",
            #             "replace_drugs": ["Препарат2", "Препарат3"]
            #         }
            #     ]
            #     }
                
            # ]

        # Расчёт препаратов по отдельности
        context["SEFromDrug"] = []
        for drug in [Drug.objects.get(id=i) for i in unique_n_drug]:
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


    def analyze_max_drug_contribution(self, incompatible_side_e, rangs_matrix, drug_ids, rangsum, side_e2id):
        """
        Формирует рекомендации по замене препаратов
        с использованием векторизованных вычислений.
        """

        # 1. Валидация входных данных
        if not isinstance(rangs_matrix, np.ndarray):
            rangs_matrix = np.array(rangs_matrix, dtype=float)
        if not isinstance(rangsum, np.ndarray):
            rangsum = np.array(rangsum, dtype=float)
        
        n_side_effect = self.n_side_effect
        logger.info(f"Анализ: {n_side_effect} побочных эффектов, {len(drug_ids)} препаратов")
        logger.debug(f"ID препаратов: {drug_ids}")

        # 2. Получение групп препаратов
        drugs_with_groups = Drug.objects.filter(id__in=drug_ids).prefetch_related('drug_groups')
        drug_names = {}
        drug_groups = {}
        group_info = {}

        for drug in drugs_with_groups:
            drug_names[drug.id] = drug.drug_name
            drug_groups[drug.id] = []
            logger.debug(f"Препарат ID={drug.id}, название={drug.drug_name}")
            
            for group in drug.drug_groups.all():
                drug_groups[drug.id].append(group.id)
                if group.id not in group_info:
                    group_info[group.id] = {
                        'name': group.dg_name, 
                        'drugs': [], 
                        'alts': [],
                        'drugs_names': []  # Добавляем список названий препаратов
                    }
                group_info[group.id]['drugs'].append(drug.id)
                group_info[group.id]['drugs_names'].append(drug.drug_name)  # Сохраняем название

        logger.debug(f"Сформирована информация о группах: {group_info}")

        # 3. Получение альтернативных препаратов
        alts = Drug.objects.filter(drug_groups__id__in=group_info.keys()).exclude(id__in=drug_ids).distinct()
        alt_names = {}
        alt_by_group = {}  # Группируем альтернативы по группам
        
        for alt in alts:
            alt_names[alt.id] = alt.drug_name
            logger.debug(f"Альтернатива ID={alt.id}, название={alt.drug_name}")
            
            for g in alt.drug_groups.all():
                if g.id in group_info:
                    group_info[g.id]['alts'].append(alt.id)
                    # Сохраняем название альтернативы для отладки
                    if 'alts_names' not in group_info[g.id]:
                        group_info[g.id]['alts_names'] = []
                    group_info[g.id]['alts_names'].append(alt.drug_name)

        logger.debug(f"Найдено альтернативных препаратов: {len(alt_names)}")
        for gid, info in group_info.items():
            logger.debug(f"Группа {info['name']}: препараты={info['drugs_names']}, альтернативы={info.get('alts_names', [])}")

        # 4. Подготовка вектора рангов для всех препаратов
        drug_rank_rows = {}
        all_drug_ids = set(drug_ids) | set(alt_names.keys())
        
        for drug_id in all_drug_ids:
            start_idx = (drug_id - 1) * n_side_effect
            end_idx = start_idx + n_side_effect
            drug_rank_rows[drug_id] = rangs_matrix[start_idx:end_idx].copy() if isinstance(rangs_matrix, np.ndarray) else np.array(rangs_matrix[start_idx:end_idx])

        # 5. Преобразование списка эффектов
        effects_to_check = incompatible_side_e
        if isinstance(incompatible_side_e, dict) and 'effects' in incompatible_side_e:
            effects_to_check = incompatible_side_e['effects']
        
        effect_indices = []
        effect_names = []
        
        for e in effects_to_check:
            effect_name = e.get('se_name') or e.get('name')
            if effect_name and effect_name in side_e2id:
                effect_indices.append(side_e2id[effect_name])
                effect_names.append(effect_name)
            else:
                logger.warning(f"Эффект '{effect_name}' не найден в side_e2id, пропускаем")

        if not effect_indices:
            logger.warning("Нет валидных эффектов для анализа")
            return {'rep_recommendations': []}

        logger.debug(f"Анализируемые эффекты: {effect_names}")
        logger.debug(f"Их индексы: {effect_indices}")

        # 6. Векторизованный поиск препаратов с максимальным вкладом
        drug_ids_list = list(drug_ids)
        
        # Создаем матрицу рангов
        ranks_subset = np.zeros((len(drug_ids_list), len(effect_indices)), dtype=float)
        for i, drug_id in enumerate(drug_ids_list):
            ranks_subset[i, :] = drug_rank_rows[drug_id][effect_indices]

        # Находим препараты с максимальным рангом
        max_indices = np.argmax(ranks_subset, axis=0)
        max_values = ranks_subset[max_indices, range(len(effect_indices))]

        # Формируем словарь max_drugs
        max_drugs = {}
        for i, eff_idx in enumerate(effect_indices):
            if max_values[i] > 0:
                drug_id = drug_ids_list[max_indices[i]]
                drug_name = drug_names.get(drug_id, f"ID_{drug_id}")
                max_drugs.setdefault(drug_id, []).append({
                    'effect': effect_names[i],
                    'value': max_values[i],
                    'drug_name': drug_name
                })

        logger.info(f"Найдено препаратов с максимальным вкладом: {len(max_drugs)}")
        for drug_id, effects in max_drugs.items():
            drug_name = drug_names.get(drug_id, f"ID_{drug_id}")
            logger.debug(f"Препарат '{drug_name}' (ID={drug_id}) максимален для эффектов: {[e['effect'] for e in effects]}")

        # 7. Формирование рекомендаций с именами
        recommendations = []
        for gid, info in group_info.items():
            logger.debug(f"Обработка группы {info['name']} (ID={gid})")
            
            group_recs = []
            for drug_id in info['drugs']:
                if drug_id in max_drugs:
                    drug_name = drug_names.get(drug_id, f"ID_{drug_id}")
                    logger.debug(f"  Препарат '{drug_name}' (ID={drug_id}) требует замены")
                    
                    old_ranks = drug_rank_rows[drug_id]
                    candidates = []
                    
                    for alt_id in info['alts']:
                        if alt_id not in drug_ids:
                            alt_name = alt_names.get(alt_id, f"ID_{alt_id}")
                            alt_ranks = drug_rank_rows[alt_id]
                            new_total = rangsum - old_ranks + alt_ranks
                            
                            if np.all(new_total < 1.0):
                                candidates.append(alt_name)
                                logger.debug(f"    Подходит альтернатива: {alt_name}")
                            else:
                                # Логируем, почему не подходит
                                max_new = np.max(new_total)
                                logger.debug(f"    Альтернатива {alt_name} не подходит (максимальная совместимость: {max_new:.3f} >= 1.0)")
                    
                    if candidates:
                        group_recs.append({
                            'drug_name': drug_name,
                            'replace_drugs': candidates
                        })
                        logger.info(f"Для препарата '{drug_name}' найдено {len(candidates)} альтернатив: {candidates}")
                    else:
                        logger.debug(f"  Для препарата '{drug_name}' не найдено подходящих альтернатив")
                else:
                    logger.debug(f"  Препарат {drug_names.get(drug_id, f'ID_{drug_id}')} не требует замены")

            if group_recs:
                recommendations.append({
                    'group_name': info['name'],
                    'drugs': group_recs
                })
                logger.info(f"Для группы '{info['name']}' сформировано {len(group_recs)} рекомендаций")

        logger.info(f"Всего сформировано {len(recommendations)} групп с рекомендациями")
        logger.debug(f"Итоговые рекомендации: {recommendations}")

        return recommendations


class CalculatorMP(BaseCalculator):
    """Оптимизированная реализация для многопроцессорности."""

    def __init__(self):
        """Инициализация калькулятора рангов для многопроцессности."""
        logger.debug("Загрузка данных для CalculatorMP")

        self.drugs = list(Drug.objects.order_by('index'))
        self.n_drug = len(self.drugs)
        self.drug_names = {drug.id: drug.drug_name for drug in self.drugs}
        self.drug_pk_to_index = {drug.pk: drug.id for drug in self.drugs}
        self.drug_name_to_index = {drug.drug_name: drug.id
                                   for drug in self.drugs}

        self.side_effects = list(SideEffect.objects.order_by('index'))
        self.n_side_effects = len(self.side_effects)
        self.se_names = {se.id: se.se_name for se in self.side_effects}

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
            matrix = np.zeros((self.n_drug, self.n_side_effects), dtype=np.float32)
            for r in drug_side_effects:
                drug_idx = r.drug.id - 1
                se_idx = r.side_effect.id - 1
                matrix[drug_idx, se_idx] = float(getattr(r, rank_name, 0.0))
            self.ranks_matrices[rank_name] = matrix

        # Кэш побочных эффектов для каждого лекарства
        self.drug_side_effects_cache = defaultdict(list)
        for r in drug_side_effects:
            self.drug_side_effects_cache[r.drug.id].append({
                'se_name': r.side_effect.se_name,
                'rank': float(getattr(r, self._DEFAULT_RANK_NAME, 0.0))
            })

        logger.debug(
            f'CalculatorMP готов: {self.n_drug} ЛС, {self.n_side_effects} ПЭ, '
            f'ранги: {self.available_ranks}'
        )

    def calculate(self, rank_name=None, n_drug=None):
        """Вычисление БЕЗ обращений к БД — только работа с памятью."""
        if n_drug is None:
            n_drug = []
        if rank_name is None or rank_name not in self.ranks_matrices:
            rank_name = self._DEFAULT_RANK_NAME

        non_zero_n_drug = [self.drug_pk_to_index[pk] for pk in n_drug if pk != 0]
        unique_n_drug = list(set(non_zero_n_drug))
        num_drugs = len(unique_n_drug)

        if num_drugs == 0:
            return self._empty_result()

        matrix = self.ranks_matrices[rank_name]
        drug_indices_0based = [idx - 1 for idx in unique_n_drug]
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
            'compatibility_fortran': classification
        }

        # Распределение побочных эффектов по классам
        side_effects = []
        for k in range(self.n_side_effects):
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
            {"compatibility": "compatible", 'effects': []},
            {"compatibility": "caution", 'effects': []},
            {"compatibility": "incompatible", 'effects': []},
        ]

        side_effects.sort(key=lambda x: x['rank'], reverse=True)
        for effect in side_effects:
            cls = effect.pop('class')
            context['side_effects'][cls - 1]['effects'].append(effect)

        # Анализ потенциальных лекарств
        drugs_class_2, drugs_class_3 = [], []

        for j in range(self.n_drug):
            if (j + 1) not in unique_n_drug:
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
            {"compatibility": 'caution', "drugs": [d['name']
                                                 for d in drug_array2]},
            {"compatibility": 'incompatible', "drugs": [d['name']
                                                        for d in drug_array3]},
        ]

        # Информация о лекарствах и их побочных эффектах
        context['drugs'] = [self.drug_names[i] for i in unique_n_drug]
        context["SEFromDrug"] = [
            {
                'd_name': self.drug_names[i],
                'effects': self.drug_side_effects_cache[i]
            } for i in unique_n_drug
        ]

        return context

    def _empty_result(self):
        """Результат для пустой комбинации."""
        return {
            'rank_iteractions': 0.0,
            'compatibility_fortran': 'compatible',
            'side_effects': [
                {"compatibility": "compatible", 'effects': []},
                {"compatibility": "caution", 'effects': []},
                {"compatibility": "incompatible", 'effects': []},
            ],
            'combinations': [
                {"compatibility": 'cause', "drugs": []},
                {"compatibility": 'incompatible', "drugs": []},
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
