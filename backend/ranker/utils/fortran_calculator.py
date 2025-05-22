"""Модуль выдуль не посредственного вычисления."""

from types import MappingProxyType
import logging

import numpy as np

from drugs.models import (Drug,
                          SideEffect,
                          DrugSideEffect)

# from ranker.models import (DrugCHF,
#                            DiseaseCHF)


logger = logging.getLogger('fortran')


class FortranCalculator:
    """
    Вычислитель рангов.

    Поля:
        - n_j - число ЛС.
        - n_k - число ПД.
    """

    _DEFAULT_FILENAME = 'rangbase.txt'

    @classmethod
    def get_default_filename(cls):
        """Метод получение защищённой кностанты _DEFAULT_FILENAME."""
        return cls._DEFAULT_FILENAME

    IDX2FILENAME = MappingProxyType({
        'rangbase.txt': 'rang_base',
        'rangm1.txt': 'rang_m1',
        'rangf1.txt': 'rang_f1',
        'rangfreq.txt': 'rang_freq',
        'rangm2.txt': 'rang_m2',
        'rangf2.txt': 'rang_f2'
    })

    def __init__(self):
        """Конструктор."""
        self.n_j = Drug.objects.count() + 1
        self.n_k = SideEffect.objects.count()

    def calculate(self, base_dir, file_name, nj):
        """
        Метод непосредственного вычисления рангов.

        Для вычисления загружаются данные из выбранного
        файла file_name, которой соотвествует выбранной
        группе случаев с пациентами:
            - rangbase.txt - Общий;
            - rangm1.txt – Мужчины до 65;
            - rangf1.txt – Женщины до 65;
            - rangfreq.txt – Нормальный;
            - rangm2.txt – Мужчины после 65;
            - rangf2.txt – Женщины после 65.
        """
        logger.debug(f'Drug.objects.count() = {Drug.objects.count()}')
        logger.debug(f'SideEffect.objects.count() = {SideEffect.objects.count()}')

        logger.debug(f'self.n_j = {self.n_j}')
        logger.debug(f'self.n_k = {self.n_k}')

        logger.debug(f'nj = {nj}')

        non_zero = list(filter(lambda x: x != 0, nj))

        # Вычисление рангов взаимодействий и эффектов
        rang1 = np.zeros((self.n_j, self.n_k))
        rangsum = np.zeros(self.n_k)
        new_rangsum = np.zeros(self.n_k)
        ramax = np.zeros(self.n_k)
        num = np.zeros(self.n_k)
        nom = np.zeros(self.n_k)

        # if file_name == None:
        #     file_name = 'rangbase.txt'
        # file_path = os.path.join(base_dir, 'txt_files_db', file_name)

        # with open(file_path, 'r') as file:
        #     rangs = np.array([float(line.strip())
        #                     for line in file.readlines()])

        if file_name is None:
            file_name = self.get_default_filename()

        logger.debug(f'file_name = {file_name}')

        rangs = [getattr(rang, self.IDX2FILENAME[file_name])
                 for rang in DrugSideEffect.objects.order_by('id')]

        logger.debug(f'len(rangs) = {len(rangs)}')

        # Составление таблицы рангов и эффектов для отдельных ЛС
        for j in range(1, self.n_j):
            for k in range(1, self.n_k):
                rang1[j, k] = rangs[self.n_k * (j - 1) + (k - 1)]

        for k in range(1, self.n_k):
            rang1[0, k] = 0.0

        # Вычисление максимального ранга по эффектам для заданного набора ЛС
        for k in range(1, self.n_k):
            rangsum[k] = sum(rang1[int(nj[m]), k] for m in range(self.n_j))

        # Максимальный ранг по совокупности эффектов
        ramax[0] = rangsum[0]
        for k in range(1, self.n_k):
            ramax[k] = max(ramax[k - 1], rangsum[k])

        ram = ramax[self.n_k - 1]

        for k in range(1, self.n_k):
            if rangsum[k] >= 1.0:
                num[k] = k

        # Классификация суммарных рангов воздействий
        if ram >= 1.0:
            classification = 'incompatible'         # 'Запрещено'
        elif ram >= 0.5 and ram < 1.0:
            classification = 'caution'              # 'Под наблюдением врача'
        else:
            classification = 'compatible'           # 'Разрешено'

        # Добавляем описание в контекст
        context = {
            'rank_iteractions': round(float(ram), 2),
            'сompatibility_fortran': classification
        }

        # Распределение рангов по всей совокупности эффектов
        side_effects = []
        for k in range(1, self.n_k):
            if rangsum[k] >= 1.0:
                nom[k] = 3
            elif 0.5 <= rangsum[k] < 1.0:
                nom[k] = 2
            else:
                nom[k] = 1

            # Получение значения name из базы данных по индексу k
            disease = SideEffect.objects.get(index=k)

            # Сохранение названия и значения в контексте
            side_effects.append({
                'se_name': disease.se_name,
                'class': int(nom[k]),
                'rank': round(float(rangsum[k]), 2)
            })

        # Фильтрация по классам
        context.update({'side_effects': [
            {"сompatibility": "compatible",
            'effects': []},
            {"сompatibility": "caution",
            'effects': []},
            {"сompatibility": "incompatible",
            'effects': []},
        ]})

        side_effects = sorted(side_effects, key=lambda x: x['rank'], reverse=True)

        for side_effect in side_effects:
            if side_effect['class'] == 1:
                del side_effect['class']
                context['side_effects'][0]['effects'].append(side_effect)
            elif side_effect['class'] == 2:
                del side_effect['class']
                context['side_effects'][1]['effects'].append(side_effect)
            elif side_effect['class'] == 3:
                del side_effect['class']
                context['side_effects'][2]['effects'].append(side_effect)

        # Анализ потенциальных ЛС
        drugs_class_1, drugs_class_2, drugs_class_3 = [], [], []
        for j in range(1, self.n_j):
            if j not in nj:
                for k in range(1, self.n_k):
                    new_rangsum[k] = rangsum[k] + rang1[j, k]

                drugs_class = 0
                for k in range(1, self.n_k):
                    if new_rangsum[k] >= 1.0 and drugs_class < 3:
                        drugs_class = 3
                    elif 0.5 <= new_rangsum[k] < 1.0 and drugs_class < 2:
                        drugs_class = 2
                    elif drugs_class < 1:
                        drugs_class = 1

                if drugs_class == 1:
                    drugs_class_1.append(j)
                elif drugs_class == 2:
                    drugs_class_2.append(j)
                else:
                    drugs_class_3.append(j)

        drug_array2 = []
        for k in range(1, len(drugs_class_2)):
            drug = Drug.objects.get(index=drugs_class_2[k])
            drug_array2.append({'name': drug.drug_name, 'class': 2})        

        drug_array3 = []
        for k in range(1, len(drugs_class_3)):
            drug = Drug.objects.get(index=drugs_class_3[k])
            drug_array3.append({'name': drug.drug_name, 'class': 3})

        context['combinations'] = [
            {"сompatibility": 'cause',
                "drugs": [item['name'] for item in drug_array2]},
            {"сompatibility": 'incompatible',
                "drugs": [item['name'] for item in drug_array3]},]
        context['drugs'] = [Drug.objects.get(id=i).drug_name
                            for i in non_zero]
        return context
