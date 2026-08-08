"""
combination_checker/services/checker.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import itertools

import numpy as np

from combination_checker.services.loader import CheckerDataset
from ranker.utils.fortran_calculator import FortranCalculator, RANG_LIMIT


@dataclass(slots=True)
class CombinationResult:
    drug_ids: list[int]
    drug_names: list[str]
    max_rank: float


@dataclass(slots=True)
class CombinationStats:
    checked: int
    found: int
    pruned: int


class CombinationChecker:
    """
    Поиск несовместимых комбинаций.

    Алгоритм:

        1. Проверяем пары.
        2. Только разрешённые пары могут участвовать
           в тройках.
        3. Только тройки без запрещённых подкомбинаций
           могут участвовать в комбинациях размера 4.
        4. И так далее до max_size.

    """

    def __init__(
        self,
        *,
        dataset: CheckerDataset,
        calculator: FortranCalculator,
        max_size: int,
        on_result: Callable[[CombinationResult], None] | None = None,
        on_progress: Callable[[int], None] | None = None,
        is_cancelled: Callable[[], bool] | None = None,
    ):
        self.dataset = dataset
        self.calculator = calculator
        self.max_size = max_size
        self.on_result = on_result
        self.on_progress = on_progress
        self.is_cancelled = is_cancelled

        self.rank_matrix = dataset.rank_matrix
        self.n_drugs = self.rank_matrix.shape[0]
        self.n_side_effects = self.rank_matrix.shape[1]

        self.checked = 0
        self.found = 0
        self.pruned = 0

        self.blocked_combinations: set[tuple[int, ...]] = set()

        self._last_progress = -1
        self._progress_throttle = 10000   # обновление раз в 1000 проверок
        self._next_progress_update = 0

        # ---------- готовим быстрые структуры для нормализации ----------
        self._do_normalize = calculator.normalize
        self._do_cap = calculator.cuttoff_not_life_threats_side_e

        if self._do_normalize:
            self._canceling_groups = [
                [idx - 1 for idx in group]
                for group in calculator.canceling_groups
            ]
        else:
            self._canceling_groups = []

        if self._do_cap:
            # СНАЧАЛА создаём маску (булев массив)
            self._non_life_mask = np.array([
                not dataset.life_threatening_map.get(se_id, True)
                for se_id in range(1, self.n_side_effects + 1)
            ], dtype=bool)
            self._rang_limit = RANG_LIMIT
            # ПОТОМ на её основе строим вектор лимитов
            self._limit_vec = np.where(self._non_life_mask, self._rang_limit, np.inf)
        else:
            self._non_life_mask = None
            self._rang_limit = None
            self._limit_vec = None

    # -------------------------------------------------------------------
    # Быстрая нормализация + кэпирование (in‑place)
    # -------------------------------------------------------------------
    def _fast_normalized_max(self, rank: np.ndarray) -> float:
        if self._do_normalize:
            orig_rank = rank.copy()      # исходные значения, не меняются
            for group in self._canceling_groups:
                vals = orig_rank[group]  # берём из оригинала
                total = vals.sum()
                if total > 0:
                    rank[group] = np.square(vals) / total  # пишем в rank
        if self._do_cap:
            np.minimum(rank, self._limit_vec, out=rank)
        return float(rank.max()) if rank.size else 0.0

    # -------------------------------------------------------------------
    # Проверка запрещённых подмножеств
    # -------------------------------------------------------------------
    def _has_blocked_subset(self, combo: tuple[int, ...]) -> bool:
        n = len(combo)
        for r in range(2, n):
            for sub in itertools.combinations(combo, r):
                if sub in self.blocked_combinations:
                    return True
        return False

    # -------------------------------------------------------------------
    # Проверка одной комбинации (принимает уже готовый массив рангов)
    # -------------------------------------------------------------------
    def _check_rank(self, rank: np.ndarray) -> tuple[bool, float]:
        # Нормализация и cap не должны менять исходную сумму.
        # Исходный rank используется дальше для построения комбинаций.
        rank_for_check = rank.copy()

        max_val = self._fast_normalized_max(rank_for_check)

        self.checked += 1
        self._notify_progress()

        return max_val >= 1.0, max_val

    def _notify_result(self, drug_indices: tuple[int, ...], max_rank: float) -> None:
        self.found += 1
        if self.on_result:
            drug_ids = [self.dataset.drug_ids[i] for i in drug_indices]
            drug_names = [self.dataset.drug_names[di] for di in drug_ids]
            self.on_result(CombinationResult(drug_ids=drug_ids, drug_names=drug_names, max_rank=max_rank))

    def _notify_progress(self) -> None:
        if self.on_progress and self.checked >= self._next_progress_update:
            self._next_progress_update = self.checked + self._progress_throttle
            self.on_progress(self.checked)

    def _check_cancelled(self) -> None:
        if self.is_cancelled and self.is_cancelled():
            raise InterruptedError("Combination checking cancelled.")

    # -------------------------------------------------------------------
    # Генерация разрешённых комбинаций размера size
    # -------------------------------------------------------------------
    def _generate_pairs(self):
        allowed = []
        n = self.n_drugs
        for idx, combo in enumerate(itertools.combinations(range(n), 2)):
            if idx % 1000 == 0:          # проверка отмены раз в 1000 пар
                self._check_cancelled()

            i, j = combo
            rank = self.rank_matrix[i] + self.rank_matrix[j]   # поэлементное сложение
            incompatible, max_r = self._check_rank(rank)
            if incompatible:
                self.pruned += 1
                self.blocked_combinations.add(combo)
                self._notify_result(combo, max_r)
            else:
                allowed.append((combo, rank.copy()))
        return allowed

    # -------------------------------------------------------------------
    # Основной цикл
    # -------------------------------------------------------------------
    def run(self) -> CombinationStats:
        self._reset()

        # Уровень 2 – пары
        current_level = self._generate_pairs()

        current_size = 2
        while current_size < self.max_size and current_level:
            self._check_cancelled()
            current_size += 1
            next_level: list[tuple[tuple[int, ...], np.ndarray]] = []

            for combo, rank_sum in current_level:
                last_idx = combo[-1]
                for new_idx in range(last_idx + 1, self.n_drugs):
                    candidate = combo + (new_idx,)
                    if self._has_blocked_subset(candidate):
                        self.pruned += 1
                        continue

                    # инкрементальная сумма
                    new_rank = rank_sum + self.rank_matrix[new_idx]
                    incompatible, max_r = self._check_rank(new_rank)
                    if incompatible:
                        self.pruned += 1
                        self.blocked_combinations.add(candidate)
                        self._notify_result(candidate, max_r)
                    else:
                        # сохраняем копию сырой суммы
                        next_level.append((candidate, new_rank.copy()))

            current_level = next_level

        return CombinationStats(checked=self.checked, found=self.found, pruned=self.pruned)

    def _reset(self):
        self.checked = 0
        self.found = 0
        self.pruned = 0
        self.blocked_combinations.clear()
        self._last_progress = -1