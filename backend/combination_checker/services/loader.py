"""Load all data required by the combination checker."""

from dataclasses import dataclass

import numpy as np

from drugs.models import Drug, DrugSideEffect, SideEffect
from ranker.utils.fortran_calculator import FortranCalculator


@dataclass(slots=True)
class CheckerDataset:
    drug_ids: list[int]
    drug_names: dict[int, str]
    side_effect_names: list[str]
    rank_matrix: np.ndarray
    life_threatening_map: dict[int, bool]
    canceling_groups: list[list[int]]
    n_drug: int
    n_side_effect: int


class DataLoader:
    def __init__(self, calculator: FortranCalculator, rank_name: str):
        self.calculator = calculator
        self.rank_name = rank_name

    def load(self) -> CheckerDataset:
        drug_ids, drug_names = self._load_drugs()
        side_effects = self._load_side_effects()
        rank_matrix = self._build_rank_matrix(drug_ids, [se[0] for se in side_effects])
        life_map = {se_id: is_life for se_id, _, is_life in side_effects}
        canceling_groups = self.calculator.canceling_groups
        return CheckerDataset(
            drug_ids=drug_ids,
            drug_names=drug_names,
            side_effect_names=[se_name for _, se_name, _ in side_effects],
            rank_matrix=rank_matrix,
            life_threatening_map=life_map,
            canceling_groups=canceling_groups,
            n_drug=len(drug_ids),
            n_side_effect=len(side_effects),
        )

    def _load_drugs(self) -> tuple[list[int], dict[int, str]]:
        drugs = Drug.objects.only("id", "drug_name").order_by("id")
        ids = [drug.id for drug in drugs]
        names = {drug.id: drug.drug_name for drug in drugs}
        return ids, names

    def _load_side_effects(self) -> list[tuple[int, str, bool]]:
        side_effects = SideEffect.objects.only(
            "id", "se_name", "is_life_threatening"
        ).order_by("id")
        return [
            (se.id, se.se_name, se.is_life_threatening)
            for se in side_effects
        ]

    def _build_rank_matrix(
        self,
        drug_ids: list[int],
        side_effect_ids: list[int],
    ) -> np.ndarray:
        n_drug = len(drug_ids)
        n_side = len(side_effect_ids)

        if n_drug != self.calculator.n_drug or n_side != self.calculator.n_side_effect:
            raise ValueError(
                "Database dimensions do not match FortranCalculator: "
                f"DB=({n_drug}, {n_side}), "
                f"calculator=({self.calculator.n_drug}, {self.calculator.n_side_effect})."
            )

        drug_index = {drug_id: index for index, drug_id in enumerate(drug_ids)}
        side_index = {side_id: index for index, side_id in enumerate(side_effect_ids)}
        matrix = np.zeros((n_drug, n_side), dtype=np.float64)

        rows = DrugSideEffect.objects.order_by("drug_id", "side_effect_id").values_list(
            "drug_id", "side_effect_id", self.rank_name
        )

        seen = set()
        for drug_id, side_effect_id, value in rows:
            if drug_id not in drug_index or side_effect_id not in side_index:
                continue
            key = (drug_id, side_effect_id)
            if key in seen:
                raise ValueError(f"Duplicate DrugSideEffect row: {key}")
            seen.add(key)
            matrix[drug_index[drug_id], side_index[side_effect_id]] = value

        expected = n_drug * n_side
        if len(seen) != expected:
            raise ValueError(
                f"Incomplete DrugSideEffect matrix: {len(seen)} of {expected} pairs present."
            )
        return matrix

    def _load_canceling_groups(self) -> list[list[int]]:
        if not self.calculator.normalize:
            return []
        return self.calculator.canceling_groups or []
