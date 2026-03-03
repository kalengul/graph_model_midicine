"""Модуль генерации таблицы."""

import logging
from io import BytesIO
from itertools import combinations
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.utils import timezone

from ranker.utils.fortran_calculator import get_calculator
from ranker.utils.check_banned import DrugPairChecker
# from ranker.constants import RANK_NAMES
from drugs.models import Drug, BannedDrugPair
from contraindications.models import Contraindication


logger = logging.getLogger('fortran')
RANK_NAMES = ['rang_base']


class ExcelTableGenerater():
    """Генератор Excel-таблиц."""

    DRUG = 'ЛС'
    LEFT = 1
    RIGHT = 5
    STOP_VALUE = 300000
    ISTOP_VALUE = 300000
    DRUG1, DRUG2 = 'ЛС 1', 'ЛС 2'
    DRUGS = 'Списки ЛС'
    REASON = 'Причина запрета'
    CONTRAINDICATION = 'Противопоказания'
    WEIGHT = 'Вес Противопоказаний'
    INCOMPATIBLE = 'incompatible'
    MULTIPROCESSING = True

    def __init__(self):
        """Инициализатор."""
        self.columns = [self.DRUG]
        self.columns.extend(RANK_NAMES)
        self.ids2drug = {drug.pk: drug.drug_name
                         for drug in Drug.objects.order_by('id')}
        self.drug2ids = {value: key for key, value in self.ids2drug.items()}
        self.calculator = get_calculator(True)
        self.banned_checker = DrugPairChecker()

    def generate_rank_table(self):
        """Генерация таблицы совместимости ЛС на основе рангов."""
        logger.debug('вход в метод генерации ранговой таблицы')
        compatible_rows = []
        incompatible_rows = []

        counters = dict.fromkeys(range(self.LEFT, self.RIGHT+1), 0)
        icounters = dict.fromkeys(range(self.LEFT, self.RIGHT+1), 0)

        incompatible_combinations = set()

        counter = 0
        incompatible_counter = 0
        repeat_incompatible_counter = 0
        for r in range(self.LEFT, self.RIGHT+1):
            drug_combinations = list(combinations(
                sorted(self.drug2ids.keys()), r))

            for drugs in drug_combinations:
                if counter % 1000 == 0 and counter != 0:
                    print('counter =', counter)

                current_set = set(drugs)

                if any(set(incomp).issubset(current_set)
                       for incomp in incompatible_combinations):
                    repeat_incompatible_counter += 1
                    continue

                ids = [self.drug2ids[id] for id in drugs]

                combination_length = len(ids)

                if (counters[combination_length] +
                    icounters[combination_length]
                        >= self.STOP_VALUE + self.ISTOP_VALUE):
                    break

                copy_ids = ids[:]

                while len(ids) < self.calculator.n_k:
                    ids.append(0)

                incompatible_row = None
                compatible_row = None
                for rank in RANK_NAMES:
                    if (self.banned_checker.check_banned(copy_ids)
                        and not any(set(incomp).issubset(current_set)
                                    for incomp in incompatible_combinations)):
                        incompatible_row = {self.DRUG: ', '.join(drugs)}
                        incompatible_row[rank] = self.INCOMPATIBLE
                        incompatible_combinations.add(drugs)
                        incompatible_counter += 1
                        continue
                    result = self.calculator.calculate(rank_name=rank, nj=ids)

                    compatibility = result['compatibility_fortran']

                    if compatibility == self.INCOMPATIBLE:
                        incompatible_row = {self.DRUG: ', '.join(drugs)}
                        incompatible_combinations.add(drugs)
                        incompatible_row[rank] = compatibility
                        incompatible_counter += 1
                    else:
                        compatible_row = {self.DRUG: ', '.join(drugs)}
                        compatible_row[rank] = compatibility

                counter += 1

                if compatible_row:
                    counters[combination_length] += 1

                if incompatible_row:
                    icounters[combination_length] += 1

                if (compatible_row
                        and self.STOP_VALUE > counters[combination_length]):
                    compatible_rows.append(compatible_row)

                if (incompatible_row
                        and self.ISTOP_VALUE > icounters[combination_length]):
                    incompatible_rows.append(incompatible_row)

        if not compatible_rows:
            logger.warning("Сгенерирован пустой список строк. "
                           "Создаем минимальный DataFrame")
            compatible_rows = [{"ЛС": "Нет данных"}]
            for rank in RANK_NAMES:
                compatible_rows[0][rank] = "Нет данных"

        compatible_df = pd.DataFrame(compatible_rows, columns=self.columns)
        incompatible_df = pd.DataFrame(incompatible_rows, columns=self.columns)
        logger.debug(f"DataFrame содержит {len(compatible_df)} строк "
                     "и {len(df.columns)} столбцов")

        if compatible_df.isnull().values.any():
            logger.error("DataFrame содержит NaN значения!")
            compatible_df = compatible_df.fillna("")

        if incompatible_df.isnull().values.any():
            logger.error("DataFrame содержит NaN значения!")
            incompatible_df = incompatible_df.fillna("")

        print('incompatible_df', incompatible_df.head())
        print('несовместимых сочетаний', incompatible_counter)
        print('повторений несовместимых сочетаний',
              repeat_incompatible_counter)
        return compatible_df, incompatible_df

    def generate_banned_pair_table(self):
        """Генерация таблицы с запрещёнными сочетаниями."""
        rows = []

        for pair in BannedDrugPair.objects.all():
            row = {
                self.DRUG1: pair.first_drug,
                self.DRUG2: pair.second_drug,
                self.REASON: pair.comment}
            rows.append(row)

        df = pd.DataFrame(rows, columns=[self.DRUG1, self.DRUG2, self.REASON])

        return df

    def generate_contraindication_table(self):
        """Генерация таблицы противопоказаний."""
        rows = []

        drugs = list(
            Drug.objects.prefetch_related('contraindications').order_by('id'))
        drug_columns = [drug.drug_name for drug in drugs]

        contraindications_dict = {}

        for drug in drugs:
            contraindications_dict[drug.id] = set(
                c.id for c in drug.contraindications.all()
            )

        contraindications = list(Contraindication.objects.all())

        for contra in contraindications:
            row = {self.CONTRAINDICATION: contra.name}
            for col, drug in zip(drug_columns, drugs):
                found = contra.id in contraindications_dict.get(drug.id, set())
                row[col] = '+' if found else '-'
            rows.append(row)

        df = pd.DataFrame(rows,
                          columns=[self.CONTRAINDICATION, *drug_columns])

        return df

    def generate_tables(self):
        """Формирование тома с таблицами."""
        rank_df, irank_df = self.generate_rank_table()
        pair_df = self.generate_banned_pair_table()
        contra_df = self.generate_contraindication_table()

        logger.debug(f"Сгенерирован DataFrame с {len(rank_df)} строками "
                     f"и {len(rank_df.columns)} столбцами")

        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            rank_df.to_excel(writer, sheet_name='совместимые сочетания',
                             index=False)
            irank_df.to_excel(writer, sheet_name='несовместимые сочетания',
                              index=False)
            pair_df.to_excel(writer, sheet_name='запрещённые сочетания ЛС',
                             index=False)
            contra_df.to_excel(writer, sheet_name='противопоказания',
                               index=False)

        path = (
            Path(settings.GENERATED_TABLES)
            / f'tables_{timezone.now().strftime("%Y.%m.%d_%H-%M-%S")}.xlsx')
        with open(path, 'wb') as f:
            f.write(output.getvalue())

        output.seek(0)
        return output
