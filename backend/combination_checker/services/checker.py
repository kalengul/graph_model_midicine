"""
combination_checker/services/checker.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import itertools

from combination_checker.services.loader import CheckerDataset
from ranker.utils.fortran_calculator import FortranCalculator

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

    Таким образом, если малая комбинация уже запрещена,
    все её расширения автоматически отбрасываются.
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

        # Состояние перебора (для рекурсивного DFS уровня 2)
        self.current_indices: list[int] = []
        self.current_rank = np.zeros(self.n_side_effects, dtype=np.float64)

        self.checked = 0
        self.found = 0
        self.pruned = 0

        # Запрещённые комбинации (отсортированные кортежи индексов)
        self.blocked_combinations: set[tuple[int, ...]] = set()

        self._last_progress = -1

    # ----------------------------------------------------------
    # Вспомогательные методы
    # ----------------------------------------------------------
    def _push_drug(self, drug_index: int) -> None:
        self.current_indices.append(drug_index)
        self.current_rank += self.rank_matrix[drug_index]

    def _pop_drug(self) -> None:
        drug_index = self.current_indices.pop()
        self.current_rank -= self.rank_matrix[drug_index]

    def _normalized_rank(self, rank: np.ndarray) -> np.ndarray:
        """Нормализует и копирует rank, не изменяя исходный rank_sum."""
        result = rank.copy()

        if self.calculator.normalize:
            result = self.calculator._apply_canceling_normalization(result)

        if self.calculator.cuttoff_not_life_threats_side_e:
            result = self.calculator._cap_non_life_threatening(result)

        return result

    def _max_rank(self, rank: np.ndarray) -> float:
        return float(rank.max()) if rank.size else 0.0

    def _current_drug_ids(self) -> list[int]:
        return [self.dataset.drug_ids[i] for i in self.current_indices]

    def _current_drug_names(self) -> list[str]:
        return [
            self.dataset.drug_names[self.dataset.drug_ids[i]]
            for i in self.current_indices
        ]

    def _notify_result(self, rank: np.ndarray) -> None:
        self.found += 1
        if self.on_result:
            self.on_result(
                CombinationResult(
                    drug_ids=self._current_drug_ids(),
                    drug_names=self._current_drug_names(),
                    max_rank=self._max_rank(rank),
                )
            )

    def _notify_progress(self) -> None:
        if self.on_progress and self.checked != self._last_progress:
            self._last_progress = self.checked
            self.on_progress(self.checked)

    def _check_cancelled(self) -> None:
        if self.is_cancelled and self.is_cancelled():
            raise InterruptedError("Combination checking cancelled.")

    # ----------------------------------------------------------
    # Новая быстрая проверка запрещённых подмножеств
    # ----------------------------------------------------------
    def _has_blocked_subset(self, combo: tuple[int, ...]) -> bool:
        """Возвращает True, если любая подкомбинация (длиной от 2 до len-1) входит в blocked_combinations."""
        n = len(combo)
        # Для n=2 подкомбинаций быть не может, но метод всё равно безопасен
        for r in range(2, n):          # подкомбинации длиной 2,3,…,n-1
            for sub in itertools.combinations(combo, r):
                if sub in self.blocked_combinations:
                    return True
        return False

    # ----------------------------------------------------------
    # Проверка текущей комбинации (использует self.current_indices / rank)
    # ----------------------------------------------------------
    def _check_current(self) -> tuple[bool, np.ndarray]:
        """Возвращает (is_incompatible, normalized_rank)."""
        rank = self._normalized_rank(self.current_rank)
        self.checked += 1
        self._notify_progress()
        return self._max_rank(rank) >= 1.0, rank

    # ----------------------------------------------------------
    # Рекурсивный перебор для одного размера (возвращает пары (tuple, rank_sum))
    # ----------------------------------------------------------
    def _check_level(self, size: int) -> list[tuple[tuple[int, ...], np.ndarray]]:
        """
        Перебирает все комбинации размера `size`.
        Возвращает список разрешённых комбинаций вместе с их векторами‑суммами рангов.
        """
        allowed: list[tuple[tuple[int, ...], np.ndarray]] = []

        def dfs(start_index: int):
            self._check_cancelled()
            current_size = len(self.current_indices)

            if current_size == size:
                combo = tuple(self.current_indices)
                # Для пар подмножеств нет, но проверка не повредит
                if size > 2 and self._has_blocked_subset(combo):
                    self.pruned += 1
                    return

                incompatible, norm_rank = self._check_current()
                if incompatible:
                    self.pruned += 1
                    self.blocked_combinations.add(combo)
                    self._notify_result(norm_rank)
                    return
                # Сохраняем комбинацию и копию текущей суммы (чтобы не испортить при дальнейших pop)
                allowed.append((combo, self.current_rank.copy()))
                return

            remaining_needed = size - current_size
            available = self.n_drugs - start_index
            if available < remaining_needed:
                return

            last_index = self.n_drugs - remaining_needed + 1
            for drug_index in range(start_index, last_index):
                self._push_drug(drug_index)
                dfs(drug_index + 1)
                self._pop_drug()
                self._check_cancelled()

        dfs(0)
        return allowed

    # ----------------------------------------------------------
    # Главный метод run
    # ----------------------------------------------------------
    def run(self) -> CombinationStats:
        self._reset()

        # Уровень 2: пары
        current_level = self._check_level(2)

        # Уровни 3, 4, ..., max_size
        current_size = 2
        while current_size < self.max_size and current_level:
            self._check_cancelled()
            current_size += 1
            next_level: list[tuple[tuple[int, ...], np.ndarray]] = []

            for combo, rank_sum in current_level:
                self._check_cancelled()
                # Последний индекс в комбинации
                last_idx = combo[-1]
                # Возможные новые индексы > last_idx
                for new_idx in range(last_idx + 1, self.n_drugs):
                    candidate_indices = combo + (new_idx,)

                    # Проверка запрещённых подмножеств (O(2^len))
                    if self._has_blocked_subset(candidate_indices):
                        self.pruned += 1
                        continue

                    # Инкрементально вычисляем сумму рангов
                    new_rank = rank_sum + self.rank_matrix[new_idx]
                    # Временно подменяем текущее состояние для _check_current
                    self.current_indices = list(candidate_indices)
                    self.current_rank = new_rank

                    incompatible, norm_rank = self._check_current()
                    if incompatible:
                        self.pruned += 1
                        self.blocked_combinations.add(candidate_indices)
                        self._notify_result(norm_rank)
                    else:
                        # Сохраняем копию вектора, чтобы не испортить при дальнейшем расширении
                        next_level.append((candidate_indices, new_rank.copy()))

            current_level = next_level

        return CombinationStats(
            checked=self.checked,
            found=self.found,
            pruned=self.pruned,
        )

    def _reset(self):
        self.checked = 0
        self.found = 0
        self.pruned = 0
        self.current_indices.clear()
        self.current_rank = np.zeros(self.n_side_effects, dtype=np.float64)
        self.blocked_combinations.clear()
        self._last_progress = -1