"""Модуль выдуль не посредственного вычисления."""

import os

import numpy as np

from ranker.models import (DrugCHF,
                           DiseaseCHF)
from medscape_api.interaction_retriever import InteractionRetriever


class FortranCalculator:
    """
    Вычислитель рангов.

    Поля:
        - n_j - число ЛС.
        - n_k - число ПД.
    """

    def __init__(self):
        """Конструктор."""
        self.n_j = DrugCHF.objects.count()
        self.n_k = DiseaseCHF.objects.count()

    def load_data_in_file(self, base_dir, file_name, nj, drug_indices2):
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
        rang1 = np.zeros((self.n_j, self.n_k))
        rangsum = np.zeros(self.n_k)
        new_rangsum = np.zeros(self.n_k)
        ramax = np.zeros(self.n_k)
        nom = np.zeros(self.n_k)

        if file_name == '':
            file_name = 'rangbase.txt'
        file_path = os.path.join(base_dir, 'txt_files_db', file_name)

        with open(file_path, 'r') as file:
            rangs = np.array([float(line.strip())
                              for line in file.readlines()])

        for j in range(1, self.n_j):
            for k in range(1, self.n_k):
                rang1[j, k] = rangs[self.n_k * (j - 1) + (k - 1)]

        for k in range(1, self.n_k):
            rangsum[k] = sum(rang1[int(nj[m]), k] for m in range(self.n_j))

        for k in range(2, self.n_k):
            ramax[k] = max(ramax[k - 1], rangsum[k])
        ram = ramax[self.n_k - 1]

        if ram >= 1.0:
            classification = 'incompatible'         # 'Запрещено'
        elif ram >= 0.5:
            classification = 'caution'              # 'Под наблюдением врача'
        else:
            classification = 'compatible'           # 'Разрешено'

        context = {
            'rank_iteractions': round(float(ram), 2),
            'сompatibility_fortran': classification
        }

        side_effects = []
        for k in range(1, self.n_k):
            if rangsum[k] >= 1.0:
                nom[k] = 3
            elif 0.5 <= rangsum[k] < 1.0:
                nom[k] = 2
            else:
                nom[k] = 1
            disease = DiseaseCHF.objects.get(index=k)
            side_effects.append({
                'se_name': disease.name,
                'class': int(nom[k]),
                'rank': round(float(rangsum[k]), 2)
            })

        context.update({'side_effects': [
            {"сompatibility": "incompatible",
             'effects': []},
            {"сompatibility": "caution",
             'effects': []},
            {"сompatibility": "compatible",
             'effects': []},
        ]})

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

                drugs_class = 1
                for k in range(1, self.n_k):
                    if new_rangsum[k] >= 1.0:
                        drugs_class = 3
                        break
                    elif 0.5 <= new_rangsum[k] < 1.0:
                        drugs_class = max(drugs_class, 2)

                if drugs_class == 1:
                    drugs_class_1.append(j)
                elif drugs_class == 2:
                    drugs_class_2.append(j)
                else:
                    drugs_class_3.append(j)

        def fetch_drugs(indices, c):
            idx2compatibility = {3: 'compatible',
                                 2: 'caution',
                                 1: 'incompatible'}
            return [{'drugs': DrugCHF.objects.get(index=i).name,
                     'сompatibility': idx2compatibility[c]}
                    for i in indices]

        context['combinations'] = [
            {"сompatibility": "compatible",
             "drugs": fetch_drugs(drugs_class_3, 3)},
            {"сompatibility": "caution",
             "drugs": fetch_drugs(drugs_class_2, 2)},
            {"сompatibility": "incompatible",
             "drugs": fetch_drugs(drugs_class_1, 1)},
        ]

        drugs = [DrugCHF.objects.get(index=i).name
                 for i in drug_indices2]
        context['compatibility_medscape'] = ''
        context['description'] = 'Справка из MedScape'
        context['drugs'] = drugs
        interactions = InteractionRetriever().get_interactions(drugs)
        if not any(interactions):
            context['drugs'] = drugs
            context['description'] = 'Справка в MedScape отсутствует',
            context['compatibility_medscape'] = (
                'Информация о совместимости в MedScape отсутствует')
        else:
            context['drugs'] = drugs
            context['description'] = interactions[0][0]['description'],
            context['compatibility_medscape'] = (
                interactions[0][0]['classification'])

        return context
