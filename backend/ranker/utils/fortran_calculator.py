"""Модуль не посредственного вычисления."""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
import json
import numpy as np

from drugs.models import Drug, SideEffect, DrugSideEffect, SideEffectsGender


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

    def calculate(self, rank_name, n_drug, gender):
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
            
            # Фильтрация по полу
            if gender and effect.se_gender.exists() and not effect.se_gender.filter(gender=gender).exists(): # type: ignore
                continue 
            
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

    def __init__(self, canceling_groups = None,
                 cuttoff_not_life_threats_side_e = True):
        """Инициализатор."""
        self.n_drug = Drug.objects.count()
        self.n_side_effect = SideEffect.objects.count()

        self.canceling_groups = self._validate_canceling_groups(canceling_groups)
        self.cuttoff_not_life_threats_side_e = cuttoff_not_life_threats_side_e

        if  self.cuttoff_not_life_threats_side_e:
            self._life_threatening_map = {se.id: se.is_life_threatening
                                        for se in SideEffect.objects.all().only('id', 'is_life_threatening')
                                        }
        logger.debug(
            f"Инициализирован калькулятор с нормализацией: {self.n_drug} ЛС, "
            f"{self.n_side_effect} ПЭ")

    def _apply_canceling_normalization(self, rangsum):
        normalized_rangsum = rangsum.copy()
        #logger.debug(f'normalized_rangsum = {normalized_rangsum}')
        for group in self.canceling_groups:
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
    
    def _cap_non_life_threatening(self, rangsum):
        """
        Ограничивает сумму рангов для нежизнеугрожающих побочных эффектов до 0.99.
        rangsum: numpy array формы (n_side_effect,)
        Возвращает новый массив с ограничениями.
        """
        
        capped = rangsum.copy()
        for se_idx, se_id in enumerate(range(1, self.n_side_effect + 1)):
            if not self._life_threatening_map.get(se_id, True):
                # Если эффект не жизнеугрожающий, ограничиваем до 0.99
                if capped[se_idx] > 0.99:
                    capped[se_idx] = 0.99
        return capped


    def calculate(self, rank_name, n_drug, gender=None):
        """
        Основной метод анализа взаимодействия препаратов.
        """
        # Валидация и предобработка
        excluded_se_ids = self._get_excluded_se_by_gender(gender)

        logger.debug(f"Введённые препараты:{n_drug}")
        logger.debug(f"Уникальные:{n_drug}")

        # Загрузка справочных данных
        id2side_e = self._load_side_effects_dict(excluded_se_ids)

        # Построение матриц рангов
        rangs_matrix, rang1, rangsum = self._build_rank_matrices(n_drug, rank_name)

        # Применение нормализации для противоположных побочных эффектов
        if self.canceling_groups:
            rangsum = self._apply_canceling_normalization(rangsum)

        # Отсечка до 0,99 для жизненеугрожающих побочных эффектов
        if self.cuttoff_not_life_threats_side_e:
            rangsum = self._cap_non_life_threatening(rangsum)

        # Классификация и побочные эффекты
        context = self._classify_and_build_side_effects(rangsum, id2side_e, excluded_se_ids)
        context['rank_iteractions'] = round(float(np.max(rangsum)), 2)

        # Исключённые препараты по группам
        excluded_drug_ids = self._get_excluded_drugs_by_groups(n_drug)

        # Анализ потенциальных ЛС
        drugs_class_2, drugs_class_3 = self._analyze_potential_drugs(
            rangs_matrix, rangsum, n_drug, excluded_drug_ids,
             excluded_se_ids, id2side_e
        )
        context.update(self._prepare_combination_context(drugs_class_2, drugs_class_3))

        # Имена выбранных препаратов
        context['drugs'] = self._get_drug_names_bulk(n_drug)

        # Если несовместимо, рекомендации
        if context["compatibility_fortran"] == "incompatible":
            # Предполагается, что _analyze_max_drug_contribution использует side_e2id
            side_e2id = {v: k for k, v in id2side_e.items()}
            context['rep_recommendations'] = self._analyze_max_drug_contribution(
                context['side_effects'][2]['effects'],
                self._get_all_ranks(rank_name),
                n_drug,
                rangsum,
                side_e2id
            )

        # Побочные эффекты по каждому препарату
        context['SEFromDrug'] = self._get_se_from_drugs(n_drug, excluded_se_ids, rank_name)

        return context
    
    def _validate_canceling_groups(self, canceling_groups):
        """Валидация и фильтрация групп нивелирования."""
        if not canceling_groups:
            return None
        if not isinstance(canceling_groups, list):
            logger.error("cancel_groups должен быть списком")
            return None
        valid_groups = []
        for group in canceling_groups:
            if not isinstance(group, list) or len(group) < 2:
                continue
            valid_indices = [idx for idx in group
                             if isinstance(idx, int) and 1 <= idx <= self.n_side_effect]
            if len(valid_indices) >= 2:
                valid_groups.append(valid_indices)
        return valid_groups
    
    def _get_excluded_se_by_gender(self, gender):
        """Возвращает множество ID побочных эффектов, исключённых по полу."""
        if not gender:
            return set()
        opposite_gender = 'woman' if gender == 'man' else 'man'
        excluded_ids = SideEffectsGender.objects.filter(gender=opposite_gender) \
            .values_list('side_effect_id', flat=True)
        return set(excluded_ids)
    
    def _load_side_effects_dict(self, excluded_se_ids):
        """Загружает все побочные эффекты и возвращает словарь {0-индекс: название}."""
        all_side_effects = SideEffect.objects.all().only('id', 'se_name')
        id2side_e = {}
        for se in all_side_effects:
            if se.id in excluded_se_ids:
                continue
            # Используем 0-индексацию для ключей
            id2side_e[se.id - 1] = se.se_name
        return id2side_e
    
    def _build_rank_matrices(self, unique_n_drug, rank_name):
        """
        Строит:
          - rangs_matrix: полная матрица рангов (n_drug x n_side_effect)
          - rang1: матрица рангов только для выбранных препаратов (len(unique_n_drug) x n_side_effect)
          - rangsum: сумма рангов по выбранным препаратам (вектор длины n_side_effect)
        """
        # Загружаем все связи DrugSideEffect, упорядоченные по drug_id и side_effect_id
        # Предполагаем, что в БД данные хранятся в порядке (drug_id, side_effect_id)
        all_ranks = list(DrugSideEffect.objects.order_by('drug_id', 'side_effect_id')
                         .values_list(rank_name, flat=True))
        # Если записей меньше, чем n_drug * n_side_effect, нужно дополнить нулями
        # Но для надёжности создадим матрицу нужного размера и заполним.
        rangs_matrix = np.zeros((self.n_drug, self.n_side_effect))
        for i, val in enumerate(all_ranks):
            drug_idx = i // self.n_side_effect
            se_idx = i % self.n_side_effect
            rangs_matrix[drug_idx, se_idx] = val

        # Индексы выбранных препаратов (0-индексация)
        selected_indices = [drug_id - 1 for drug_id in unique_n_drug]
        rang1 = rangs_matrix[selected_indices, :]
        rangsum = np.sum(rang1, axis=0)
        return rangs_matrix, rang1, rangsum
    
    def _get_all_ranks(self, rank_name):
        """Возвращает список всех рангов (для использования в _analyze_max_drug_contribution)."""
        return list(DrugSideEffect.objects.order_by('drug_id', 'side_effect_id')
                    .values_list(rank_name, flat=True))
    

    def _classify_and_build_side_effects(self, rangsum, id2side_e, excluded_se_ids):
        """Классифицирует общую комбинацию и строит список побочных эффектов по классам."""
        ram = np.max(rangsum)
        if ram >= 1.0:
            classification = 'incompatible'
        elif ram >= 0.5:
            classification = 'caution'
        else:
            classification = 'compatible'

        # Собираем все эффекты с их классами
        side_effects_by_class = {1: [], 2: [], 3: []}
        for se_idx, rank_val in enumerate(rangsum):
            if se_idx not in id2side_e:  # пропускаем исключённые по полу
                continue
            if rank_val >= 1.0:
                cls = 3
            elif rank_val >= 0.5:
                cls = 2
            else:
                cls = 1
            side_effects_by_class[cls].append({
                'se_name': id2side_e[se_idx],
                'rank': round(float(rank_val), 2),
                'class': cls
            })

        # Сортируем внутри каждого класса по убыванию ранга
        for cls in side_effects_by_class:
            side_effects_by_class[cls].sort(key=lambda x: x['rank'], reverse=True)
            # Убираем временное поле 'class'
            for item in side_effects_by_class[cls]:
                del item['class']

        context = {
            'compatibility_fortran': classification,
            'side_effects': [
                {"compatibility": "compatible", 'effects': side_effects_by_class[1]},
                {"compatibility": "caution", 'effects': side_effects_by_class[2]},
                {"compatibility": "incompatible", 'effects': side_effects_by_class[3]},
            ]
        }
        return context
    
    def _get_excluded_drugs_by_groups(self, unique_n_drug):
        """
        Возвращает множество ID препаратов (0-индексация),
        которые принадлежат к тем же группам, что и выбранные, но сами не выбраны.
        """
        if not unique_n_drug:
            return set()
        # Получаем все группы выбранных препаратов
        drugs = Drug.objects.filter(id__in=unique_n_drug).prefetch_related('drug_groups')
        group_ids = set()
        for drug in drugs:
            group_ids.update(drug.drug_groups.values_list('id', flat=True))

        if not group_ids:
            return set()

        # ID всех препаратов из этих групп, исключая выбранные
        excluded = Drug.objects.filter(drug_groups__id__in=group_ids) \
            .exclude(id__in=unique_n_drug) \
            .values_list('id', flat=True) \
            .distinct()
        return {drug_id - 1 for drug_id in excluded}
    
    def _analyze_potential_drugs(self, rangs_matrix, rangsum, unique_n_drug,
                                 excluded_drug_ids,
                                 excluded_se_ids, id2side_e):
        """
        Анализирует потенциальные ЛС, возвращает списки для классов 2 и 3.
        """
        unique_n_drug_0 = {idx - 1 for idx in unique_n_drug}
        drugs_class_2 = []
        drugs_class_3 = []

        for drug_idx in range(self.n_drug):
            # Пропускаем выбранные и исключённые
            if drug_idx in unique_n_drug_0 or drug_idx in excluded_drug_ids:
                continue

            new_rangsum = rangsum + rangs_matrix[drug_idx]

            if self.canceling_groups:
                new_rangsum = self._apply_canceling_normalization(new_rangsum)

            if self.cuttoff_not_life_threats_side_e:
                new_rangsum = self._cap_non_life_threatening(new_rangsum)

            # Класс 3
            drug_data = self._build_drug_if_has_effects(
                drug_idx, new_rangsum, id2side_e, excluded_se_ids,
                1.0, None, include_side_e=True
            )
            if drug_data:
                drugs_class_3.append(drug_data)

            # Класс 2
            drug_data = self._build_drug_if_has_effects(
                drug_idx, new_rangsum, id2side_e, excluded_se_ids,
                0.5, 1.0, include_side_e=False
            )
            if drug_data:
                drugs_class_2.append(drug_data)

        return drugs_class_2, drugs_class_3
    
    def _build_drug_if_has_effects(self, drug_idx, rangsum_vec,
                                id2side_e, excluded_se_ids,
                                threshold_min, threshold_max,
                                include_side_e=True):
        """Возвращает словарь препарата, если есть подходящие эффекты, иначе None."""
        if threshold_max is None:
            mask = rangsum_vec >= threshold_min
        else:
            mask = (rangsum_vec >= threshold_min) & (rangsum_vec < threshold_max)

        indices = np.where(mask)[0]
        if len(indices) == 0:
            return None

        side_effects = []
        if include_side_e:
            for idx in indices:
                se_id = idx + 1
                if se_id in excluded_se_ids:
                    continue
                se_name = id2side_e.get(idx)
                if se_name:
                    side_effects.append({
                        'se_name': se_name,
                        'rank': round(float(rangsum_vec[idx]), 2)
                    })
            if not side_effects:
                return None   # все эффекты оказались исключены

        return {
            'drug_index': drug_idx,
            'side_effects': side_effects
        }
    
    def _prepare_combination_context(self, drugs_class_2, drugs_class_3):
        """Преобразует списки препаратов в формат контекста."""
        # Собираем все индексы для одного запроса
        all_indices = set()
        for drug in drugs_class_2 + drugs_class_3:
            all_indices.add(drug['drug_index'] + 1)  # переводим в ID

        drug_names = self._get_drug_names_bulk(list(all_indices))

        def build_array(class_drugs, class_num):
            return [
                {
                    'name': drug_names[d['drug_index'] + 1],
                    'class': class_num,
                    'side_effects': d['side_effects']
                }
                for d in class_drugs
            ]

        drug_array2 = build_array(drugs_class_2, 2)
        drug_array3 = build_array(drugs_class_3, 3)

        return {
            'combinations': [
                {
                    "compatibility": 'caution',
                    "drugs": [{"name": d['name'], "side_effects": d['side_effects']}
                              for d in drug_array2]
                },
                {
                    "compatibility": 'incompatible',
                    "drugs": [{"name": d['name'], "side_effects": d['side_effects']}
                              for d in drug_array3]
                },
            ]
        }
    
    def _get_drug_names_bulk(self, drug_ids):
        """Возвращает словарь {drug_id: drug_name} для заданных ID."""
        if not drug_ids:
            return {}
        drugs = Drug.objects.filter(id__in=drug_ids).only('id', 'drug_name')
        return {drug.id: drug.drug_name for drug in drugs}
    
    def _get_se_from_drugs(self, unique_n_drug, excluded_se_ids, rank_name):
        """
        Возвращает список словарей с побочными эффектами для каждого выбранного препарата.
        """

        if not unique_n_drug:
            return []

        # Загружаем все связи для выбранных препаратов одним запросом
        drug_side_effects = DrugSideEffect.objects.filter(drug_id__in=unique_n_drug) \
            .select_related('side_effect') \
            .only('drug_id', 'side_effect_id', rank_name)

        # Группируем по drug_id
        effects_by_drug = defaultdict(list)
        for dse in drug_side_effects:
            if dse.side_effect.id in excluded_se_ids:
                continue
            effects_by_drug[dse.drug_id].append({
                'se_name': dse.side_effect.se_name,
                'rank': getattr(dse, rank_name)
            })

        # Преобразуем в список в порядке original unique_n_drug
        result = []
        for drug_id in unique_n_drug:
            effects = effects_by_drug.get(drug_id, [])
            # Сортируем по убыванию ранга
            # effects.sort(key=lambda x: x['rank'], reverse=True)
            result.append({
                'd_name': Drug.objects.get(id=drug_id).drug_name,
                'effects': effects
            })
        return result

    def _analyze_max_drug_contribution(self, incompatible_side_e, rangs_matrix,
                                       drug_ids, rangsum, side_e2id):
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

                            # Нормализация для групп нивелирования
                            if self.canceling_groups: 
                                new_total = self._apply_canceling_normalization(new_total)
                            # Ограничение нежизнеугрожающих эффектов
                            if self.cuttoff_not_life_threats_side_e:
                                new_total = self._cap_non_life_threatening(new_total)
                            
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
