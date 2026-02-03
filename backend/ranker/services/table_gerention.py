"""Модуль генерации таблицы."""

import logging
from io import BytesIO
from itertools import combinations

import pandas as pd
# from tqdm import tqdm

from ranker.utils.fortran_calculator import FortranCalculator
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
    STOP_VALUE = 100
    DRUG1, DRUG2 = 'ЛС 1', 'ЛС 2'
    REASON = 'Причина запрета'
    CONTRAINDICATION = 'Противопоказания'
    WEIGHT = 'Вес Противопоказаний'
    INCOMPATIBLE = 'incompatible'

    def __init__(self):
        """Инициализатор."""
        self.columns = [self.DRUG]
        self.columns.extend(RANK_NAMES)
        self.ids2drug = {drug.pk: drug.drug_name
                         for drug in Drug.objects.order_by('id')}
        self.drug2ids = {value: key for key, value in self.ids2drug.items()}
        self.calculator = FortranCalculator()
        self.banned_checker = DrugPairChecker()

    def generate_rank_table(self):
        """Генерация таблицы соместимости ЛС на основе рангов."""
        logger.debug('вход в метод генерации ранговой таблицы')
        rows = []

        counters = dict.fromkeys(range(self.LEFT, self.RIGHT+1), 0)

        incompatible_combinations = set()

        for r in tqdm(range(self.LEFT, self.RIGHT+1), ncols=80):

            drug_combinations = list(combinations(
                sorted(self.drug2ids.keys()), r))

            # print('len(drug_combinations) =', len(drug_combinations))

            for drugs in drug_combinations:
                # logger.debug('перебор комбинаций')
                current_set = set(drugs)

                print('incompatible_combinations =', incompatible_combinations)
                if any(set(incomp).issubset(current_set)
                       for incomp in incompatible_combinations):
                    logger.debug((f'Пропуск {drugs} — содержит'
                                  ' несовместимую подкомбинацию'))
                    continue

                row = {self.DRUG: ', '.join(drugs)}
                # logger.debug(f'drugs = {drugs}')
                ids = [self.drug2ids[id] for id in drugs]

                combination_length = len(ids)
                # logger.debug(f'combination_length = {combination_length}')

                if self.banned_checker.check_banned(ids):
                    # logger.debug('Есть запрещённая пара!!!')
                    continue

                # if counters[combination_length] >= self.STOP_VALUE:
                #     logger.debug('combination_length для комбинаций '
                #                  f'из {combination_length} - больше 100')
                #     break

                counters[combination_length] += 1
                # logger.debug(f'counters = {counters}')

                while len(ids) < self.calculator.n_k:
                    ids.append(0)

                # logger.debug('начало рассчёта рангов')
                for rank in RANK_NAMES:
                    # logger.debug(f'рассчёт рангов {rank}')
                    result = self.calculator.calculate(rank_name=rank, nj=ids)

                    compatibility = result['сompatibility_fortran']

                    # print('self.INCOMPATIBLE', self.INCOMPATIBLE)
                    if (compatibility != 'caution'
                            and compatibility != 'compatible'):
                        print('compatibility =', compatibility)

                    if compatibility == self.INCOMPATIBLE:
                        incompatible_combinations.add(drugs)

                    row[rank] = compatibility

                rows.append(row)

        if not rows:
            logger.warning("Сгенерирован пустой список строк. "
                           "Создаем минимальный DataFrame")
            rows = [{"ЛС": "Нет данных"}]
            for rank in RANK_NAMES:
                rows[0][rank] = "Нет данных"

        df = pd.DataFrame(rows, columns=self.columns)
        # logger.debug(f"DataFrame содержит {len(df)} строк "
        #              "и {len(df.columns)} столбцов")

        if df.isnull().values.any():
            # logger.error("DataFrame содержит NaN значения!")
            df = df.fillna("")

        return df

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
        for contra in Contraindication.objects.all():
            row = {
                self.CONTRAINDICATION: contra.name,
                self.WEIGHT: contra.weight}
            rows.append(row)

        df = pd.DataFrame(rows, columns=[self.CONTRAINDICATION, self.WEIGHT])

        return df

    def generate_tables(self):
        """Формирвание тома с таблицами."""
        rank_df = self.generate_rank_table()
        # pair_df = self.generate_banned_pair_table()
        # contra_df = self.generate_contraindication_table()

        logger.debug(f"Сгенерирован DataFrame с {len(rank_df)} строками "
                     f"и {len(rank_df.columns)} столбцами")

        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            rank_df.to_excel(writer, sheet_name='ранговая система оценивания',
                             index=False)
            # pair_df.to_excel(writer, sheet_name='запрещённые сочетания ЛС',
            #                  index=False)
            # contra_df.to_excel(writer, sheet_name='противопоказания',
            #                    index=False)

        with open('debug_tables.xlsx', 'wb') as f:
            f.write(output.getvalue())

        output.seek(0)

        return output
