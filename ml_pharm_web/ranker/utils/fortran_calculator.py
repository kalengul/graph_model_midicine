"""Модуль выдуль не посредственного вычисления."""

import os

import numpy as np

from ranker.models import (DrugCHF,
                           DiseaseCHF)


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

    def load_data_in_file(self, base_dir, file_name, nj):
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
            classification = 'Запрещено'
        elif ram >= 0.5:
            classification = 'Под наблюдением врача'
        else:
            classification = 'Разрешено'

        context = {
            'rand_iteractions': round(float(ram), 2),
            'classification_description': classification
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
                'name': disease.name,
                'class': int(nom[k]),
                'rangsum': round(float(rangsum[k]), 2)
            })

        context.update({
            'side_effects_class_1': [e for e in side_effects
                                     if e['class'] == 1],
            'side_effects_class_2': [e for e in side_effects
                                     if e['class'] == 2],
            'side_effects_class_3': [e for e in side_effects
                                     if e['class'] == 3],
        })

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
            return [{'name': DrugCHF.objects.get(index=i).name, 'class': c}
                    for i in indices]

        context.update({
            'arr_drugs_class_1': fetch_drugs(drugs_class_1, 1),
            'arr_drugs_class_2': fetch_drugs(drugs_class_2, 2),
            'arr_drugs_class_3': fetch_drugs(drugs_class_3, 3),
        })

        return context
