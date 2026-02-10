"""Модуль генерации таблицы."""

import os
import time
import logging
from io import BytesIO
from itertools import combinations
from multiprocessing import Process, Manager, Lock, Pool, cpu_count

import pandas as pd
from tqdm import tqdm


from ranker.utils.fortran_calculator import get_calculator, FortranCalculator
from ranker.utils.check_banned import DrugPairChecker
from ranker.constants import RANK_NAMES
from drugs.models import Drug, BannedDrugPair
from contraindications.models import Contraindication


logger = logging.getLogger('fortran')
# RANK_NAMES = ['rang_base']


def _incompatible_worker(args):
    """
    Воркер для обработки одной длины комбинаций.

    Аргументы:
        args (tuple): (r, drug_names, drug_pk_to_index, rank_matrix, n_k, stop_value, banned_pairs)

    Возвращает:
        tuple: (r, rows, count, total_processed)
    """
    import numpy as np
    from itertools import combinations

    r, drug_names, drug_pk_to_index, rank_matrix, n_k, stop_value, banned_pairs, rank_names = args

    def is_banned_combination(ids):
        """Проверка наличия запрещённой пары в комбинации."""
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                pair = tuple(sorted([ids[i], ids[j]]))
                if pair in banned_pairs:
                    return True
        return False

    rows = []
    count = 0
    total_processed = 0

    for drugs in combinations(drug_names, r):
        total_processed += 1

        if count >= stop_value:
            break

        ids = [drug_pk_to_index[drug] for drug in drugs]

        if is_banned_combination(ids):
            row = {'ЛС': ', '.join(drugs)}
            for rank in rank_names:
                row[rank] = 'incompatible'
            rows.append(row)
            count += 1
            continue

        nj = ids.copy()
        while len(nj) < n_k:
            nj.append(0)

        drug_indices = [drug_pk_to_index[pk] for pk in nj if pk != 0]
        unique_indices = list(set(drug_indices))
        drug_indices_0based = [idx - 1 for idx in unique_indices]

        rang1 = rank_matrix[drug_indices_0based, :]
        rangsum = np.sum(rang1, axis=0)
        ram = float(np.max(rangsum))

        if ram >= 1.0:
            row = {'ЛС': ', '.join(drugs)}
            for rank in rank_names:
                row[rank] = 'incompatible'
            rows.append(row)
            count += 1

    return r, rows, count, total_processed


class ExcelTableGenerater():
    """Генератор Excel-таблиц."""

    DRUG = 'ЛС'
    LEFT = 1
    RIGHT = 5
    STOP_VALUE = 100
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
        # self.calculator = FortranCalculator()
        self.banned_checker = DrugPairChecker()

    # @staticmethod
    # def _worker_process(r, drug_names, drug2ids, ids2drug, n_k, stop_value,
    #                     shared_rows, shared_counters, shared_incompatible,
    #                     lock, progress_queue):
    #     """
    #     Воркер-процесс для обработки комбинаций определённой длины r.

    #     Использует локальные экземпляры калькулятора
    #     и чекера для избежания проблем с pickle.
    #     """
    #     try:
    #         calculator = get_calculator(ExcelTableGenerater.MULTIPROCESSING)
    #         banned_checker = DrugPairChecker()

    #         # Локальные копии для быстрого доступа
    #         # (минимизируем обращения к Manager)
    #         local_incompatible = set()
    #         local_counters = {i: 0 for i in range(1, 6)}
    #         local_rows = []
    #         processed = 0

    #         # Загружаем актуальные несовместимые комбинации из shared-памяти
    #         with lock:
    #             local_incompatible.update(shared_incompatible)

    #         drug_combinations = list(combinations(sorted(drug_names), r))
    #         total = len(drug_combinations)

    #         for idx, drugs in enumerate(drug_combinations):
    #             # Отправляем прогресс в основной процесс
    #             if idx % 100 == 0:
    #                 progress_queue.put((r, idx, total))

    #             # Проверяем early skip по несовместимым подкомбинациям
    #             current_set = set(drugs)
    #             if any(set(incomp).issubset(current_set) 
    #                    for incomp in local_incompatible):
    #                 continue

    #             # Проверяем banned пары
    #             ids = [drug2ids[drug] for drug in drugs]
    #             if banned_checker.check_banned(ids):
    #                 continue

    #             # Проверяем лимит для текущей длины комбинации
    #             with lock:
    #                 if shared_counters[r] >= stop_value:
    #                     break
    #                 shared_counters[r] += 1
    #                 current_count = shared_counters[r]

    #             # Дополняем нулями до нужной длины для Fortran
    #             nj = ids.copy()
    #             while len(nj) < n_k:
    #                 nj.append(0)

    #             # Рассчитываем ранги
    #             row = {'ЛС': ', '.join(drugs)}
    #             is_incompatible = False

    #             for rank in RANK_NAMES:
    #                 result = calculator.calculate(rank_name=rank, nj=nj)
    #                 compatibility = result['сompatibility_fortran']
    #                 row[rank] = compatibility

    #                 if compatibility == 'incompatible':
    #                     is_incompatible = True

    #             # Сохраняем несовместимую комбинацию для других процессов
    #             if is_incompatible:
    #                 with lock:
    #                     shared_incompatible.add(drugs)
    #                 local_incompatible.add(drugs)

    #             local_rows.append(row)
    #             processed += 1

    #         # Атомарно добавляем результаты в общий список
    #         with lock:
    #             shared_rows.extend(local_rows)

    #         progress_queue.put(('DONE', r, processed, total))

    #     except Exception as e:
    #         logger.error(f"Ошибка в процессе r={r}: {e}", exc_info=True)
    #         progress_queue.put(('ERROR', r, str(e)))

    # def generate_rank_table(self):
    #     """
    #     Генерация таблицы совместимости ЛС.

    #     На основе рангов с multiprocessing.
    #     """
    #     logger.debug('Вход в метод генерации ранговой таблицы')

    #     # Создаём менеджер для общих структур
    #     with Manager() as manager:
    #         shared_rows = manager.list()
    #         shared_counters = manager.dict(
    #             {i: 0 for i in range(self.LEFT, self.RIGHT + 1)})
    #         shared_incompatible = manager.set()
    #         lock = manager.Lock()
    #         progress_queue = manager.Queue()

    #         # Запускаем процессы для каждой длины комбинаций
    #         processes = []
    #         drug_names = sorted(self.drug2ids.keys())

    #         for r in range(self.LEFT, self.RIGHT + 1):
    #             p = Process(
    #                 target=self._worker_process,
    #                 args=(
    #                     r,
    #                     drug_names,
    #                     self.drug2ids,
    #                     self.ids2drug,
    #                     self.calculator.n_k,
    #                     self.STOP_VALUE,
    #                     shared_rows,
    #                     shared_counters,
    #                     shared_incompatible,
    #                     lock,
    #                     progress_queue
    #                 ),
    #                 name=f'RankWorker-r{r}'
    #             )
    #             p.start()
    #             processes.append(p)

    #         # Отображаем прогресс в реальном времени
    #         total_progress = {r: {'done': 0, 'total': 0}
    #                           for r in range(self.LEFT, self.RIGHT + 1)}
    #         completed_processes = 0

    #         with tqdm(total=self.RIGHT - self.LEFT + 1,
    #                   desc="Обработка длин комбинаций",
    #                   ncols=80) as pbar:
    #             while completed_processes < len(processes):
    #                 while not progress_queue.empty():
    #                     msg = progress_queue.get()
    #                     if msg[0] == 'DONE':
    #                         _, r, processed, total = msg
    #                         total_progress[r]['done'] = processed
    #                         total_progress[r]['total'] = total
    #                         completed_processes += 1
    #                         pbar.update(1)
    #                         pbar.set_postfix({f'r{r}': f'{processed}/{total}'})
    #                     elif msg[0] == 'ERROR':
    #                         _, r, error = msg
    #                         logger.error(f"Процесс r={r} завершился "
    #                                      "с ошибкой: {error}")
    #                         completed_processes += 1
    #                         pbar.update(1)
    #                     elif isinstance(msg[0], int):
    #                         r, done, total = msg
    #                         total_progress[r]['done'] = done
    #                         total_progress[r]['total'] = total

    #                 # Небольшая пауза чтобы не грузить CPU
    #                 time.sleep(0.1)

    #         # Дожидаемся завершения всех процессов
    #         for p in processes:
    #             p.join(timeout=5)
    #             if p.is_alive():
    #                 logger.warning(f"Процесс {p.name} не завершился штатно,"
    #                                "принудительное завершение")
    #                 p.terminate()
    #                 p.join()

    #         # Конвертируем shared_rows в обычный список
    #         rows = list(shared_rows)

    #     # Создаём финальный DataFrame
    #     if not rows:
    #         logger.warning("Сгенерирован пустой список строк. "
    #                        "Создаём минимальный DataFrame")
    #         rows = [{"ЛС": "Нет данных"}]
    #         for rank in RANK_NAMES:
    #             rows[0][rank] = "Нет данных"

    #     df = pd.DataFrame(rows, columns=self.columns)

    #     if df.isnull().values.any():
    #         logger.warning("DataFrame содержит NaN значения, "
    #                        "заполняем пустыми строками")
    #         df = df.fillna("")

    #     logger.debug(f"Сгенерирован DataFrame с {len(df)} "
    #                  "строками и {len(df.columns)} столбцами")
    #     return df

    def generate_rank_table(self):
        """Генерация таблицы соместимости ЛС на основе рангов."""
        logger.debug('вход в метод генерации ранговой таблицы')
        rows = []

        counters = dict.fromkeys(range(self.LEFT, self.RIGHT+1), 0)

        incompatible_combinations = set()

        counter = 0
        for r in tqdm(range(self.LEFT, self.RIGHT+1), ncols=80):
            drug_combinations = list(combinations(
                sorted(self.drug2ids.keys()), r))

            # print('len(drug_combinations) =', len(drug_combinations))

            for drugs in drug_combinations:
                # logger.debug('перебор комбинаций')
                if counter % 1000 == 0 and counter != 0:
                    print('counter =', counter)

                current_set = set(drugs)

                # print('incompatible_combinations =', incompatible_combinations)
                if any(set(incomp).issubset(current_set)
                       for incomp in incompatible_combinations):
                    # logger.debug((f'Пропуск {drugs} — содержит'
                    #               ' несовместимую подкомбинацию'))
                    continue

                row = {self.DRUG: ', '.join(drugs)}
                # logger.debug(f'drugs = {drugs}')
                ids = [self.drug2ids[id] for id in drugs]

                combination_length = len(ids)
                # logger.debug(f'combination_length = {combination_length}')

                if self.banned_checker.check_banned(ids):
                    # logger.debug('Есть запрещённая пара!!!')
                    continue

                if counters[combination_length] >= self.STOP_VALUE:
                    # logger.debug('combination_length для комбинаций '
                    #              f'из {combination_length} - больше 100')
                    break

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
                    # if (compatibility != 'caution'
                    #         and compatibility != 'compatible'):
                        # print('compatibility =', compatibility)

                    if compatibility == self.INCOMPATIBLE:
                        incompatible_combinations.add(drugs)

                    row[rank] = compatibility

                counter += 1

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
        drugs = Drug.objects.order_by('id')
        columns = [f'ЛС №{drug.id}' for drug in drugs]
        for contra in Contraindication.objects.all():
            row = {
                self.CONTRAINDICATION: contra.name,
                self.WEIGHT: contra.weight}
            for col, drug in zip(columns, drugs):
                row[col] = drug
            rows.append(row)

        df = pd.DataFrame(rows, columns=[self.CONTRAINDICATION, self.WEIGHT,
                                         *columns])

        return df

    def generate_incompatible_table(self):
        """
        Генерация таблицы ТОЛЬКО с несовместимыми комбинациями ЛС.

        Использует оптимизацию: если комбинация несовместима,
        все её надмножества автоматически пропускаются (early skipping).
        """
        logger.info('Запуск генерации таблицы несовместимых комбинаций')

        is_docker = os.environ.get('DOCKER_ENV', 'false').lower() == 'true'
        is_linux = os.name == 'posix'

        if is_docker or is_linux:
            logger.info('Обнаружена среда Docker/Linux '
                        '- используем многопроцессорность')
            return self._generate_incompatible_mp()
        else:
            logger.warning('Обнаружена среда Windows '
                           '- используем синхронную версию')
            return self._generate_incompatible_sync()

    def _generate_incompatible_sync(self):
        """Синхронная версия (для нативного Windows)."""
        logger.debug('Вход в синхронную генерацию несовместимых комбинаций')
        rows = []

        counters = dict.fromkeys(range(self.LEFT, self.RIGHT + 1), 0)
        incompatible_combinations = set()

        total_processed = 0

        for r in tqdm(range(self.LEFT, self.RIGHT + 1),
                      ncols=80):
            drug_combinations = combinations(sorted(self.drug2ids.keys()), r)

            for drugs in drug_combinations:
                total_processed += 1

                if counters[r] >= self.STOP_VALUE:
                    break

                ids = [self.drug2ids[drug] for drug in drugs]
                is_incompatible = False
                row = {self.DRUG: ', '.join(drugs)}

                if (self.banned_checker.check_banned(ids) or
                    any(set(incomp).issubset(set(drugs))
                        for incomp in incompatible_combinations)):
                    is_incompatible = True
                    for rank in RANK_NAMES:
                        row[rank] = self.INCOMPATIBLE
                else:
                    calculator = get_calculator(self.MULTIPROCESSING)
                    nj = ids.copy()
                    while len(nj) < calculator.n_k:
                        nj.append(0)

                    # Рассчитываем все ранги (не прерываем — нужны все значения для таблицы)
                    for rank in RANK_NAMES:
                        result = calculator.calculate(rank_name=rank, nj=nj)
                        compatibility = result['сompatibility_fortran']
                        row[rank] = compatibility

                        if compatibility == self.INCOMPATIBLE:
                            is_incompatible = True

                if is_incompatible:
                    rows.append(row)
                    incompatible_combinations.add(drugs)
                    counters[r] += 1

        df = pd.DataFrame(
            rows or [{self.DRUG: "Нет несовместимых комбинаций",
                     **{r: "—" for r in RANK_NAMES}}],
            columns=self.columns
        ).fillna("")
        logger.info(f"Синхронно: {len(df)} несовм. комбинаций")
        return df

    def _generate_incompatible_mp(self):
        """
        Многопроцессорная версия (для Docker/Linux).

        Распараллеливает обработку по длинам комбинаций (1-5).
        Каждая длина обрабатывается в отдельном процессе.
        """
        logger.debug('Вход в многопроцессорную генерацию несовместимых комбинаций')

        calculator = get_calculator(self.MULTIPROCESSING)
        drug_names = sorted(self.drug2ids.keys())

        banned_pairs = set(
            tuple(sorted([pair.first_drug, pair.second_drug]))
            for pair in BannedDrugPair.objects.all()
        )
        logger.debug(f"Загружено {len(banned_pairs)} запрещённых пар")

        tasks = []
        for r in range(self.LEFT, self.RIGHT + 1):
            tasks.append((
                r,
                drug_names,
                calculator.drug_pk_to_index,
                calculator.ranks_matrices['rang_base'],
                calculator.n_k,
                self.STOP_VALUE,
                banned_pairs,
                RANK_NAMES
            ))

        num_processes = min(len(tasks), cpu_count())
        logger.info(
            f"Запуск {num_processes} процессов для длин "
            f"{self.LEFT}-{self.RIGHT} "
            f"(доступно ядер: {cpu_count()})"
        )

        with Pool(processes=num_processes) as pool:
            results = pool.map(_incompatible_worker, tasks)

        all_rows = []
        for r, rows, count, total_processed in results:
            all_rows.extend(rows)
            logger.info(
                f"Длина {r}: собрано {count}/{self.STOP_VALUE} "
                f"несовм. из {total_processed} обработанных"
            )

        if not all_rows:
            logger.warning("Не найдено несовместимых комбинаций")
            all_rows = [{self.DRUG: "Нет несовместимых комбинаций"}]
            for rank in RANK_NAMES:
                all_rows[0][rank] = "—"

        df = pd.DataFrame(all_rows, columns=self.columns).fillna("")

        logger.info(
            f"Многопроцессорно: {len(df)} несовм. комбинаций "
            f"(цель: {self.STOP_VALUE * len(range(self.LEFT, self.RIGHT + 1))})"
        )

        return df

    def generate_tables(self):
        """Формирвание тома с таблицами."""
        # rank_df = self.generate_rank_table()
        # pair_df = self.generate_banned_pair_table()
        # contra_df = self.generate_contraindication_table()

        # logger.debug(f"Сгенерирован DataFrame с {len(rank_df)} строками "
        #              f"и {len(rank_df.columns)} столбцами")
        incompatible_table_df = self.generate_incompatible_table()

        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # rank_df.to_excel(writer, sheet_name='ранговая система оценивания',
            #                  index=False)
            # pair_df.to_excel(writer, sheet_name='запрещённые сочетания ЛС',
            #                  index=False)
            # contra_df.to_excel(writer, sheet_name='противопоказания',
            #                    index=False)
            incompatible_table_df.to_excel(
                writer,
                sheet_name='несовместимые сочетания ЛС',
                index=False)

        with open('debug_tables.xlsx', 'wb') as f:
            f.write(output.getvalue())

        output.seek(0)

        return output
