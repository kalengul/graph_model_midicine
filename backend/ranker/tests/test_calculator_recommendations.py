"""Анализ потенциальных препаратов и рекомендации."""
import numpy as np
import pytest

from side_effects.models import DrugSideEffect


pytestmark = pytest.mark.django_db


class TestAnalyzePotentialDrugs:

    def test_no_extra_drugs(self, calculator_base, filled_db):
        three_drugs, three_side_effects = filled_db
        n_drug = [three_drugs[0].id, three_drugs[1].id]
        matrix, _, rangsum = calculator_base._build_rank_matrices(n_drug, 'rang_base')
        id2side = {se.id - 1: se.se_name for se in three_side_effects}
        c2, c3 = calculator_base._analyze_potential_drugs(
            matrix, rangsum, n_drug, set(), id2side
        )
        assert c2 == [] and c3 == []

    def test_adding_incompatible_drug(self, calculator_base, filled_db):
        three_drugs, three_side_effects = filled_db
        DrugSideEffect.objects.filter(
            drug=three_drugs[2], side_effect=three_side_effects[0]
        ).update(rang_base=1.0)
        n_drug = [three_drugs[0].id]
        matrix, _, rangsum = calculator_base._build_rank_matrices(n_drug, 'rang_base')
        id2side = {se.id - 1: se.se_name for se in three_side_effects}
        _, c3 = calculator_base._analyze_potential_drugs(
            matrix, rangsum, n_drug, set(), id2side
        )
        assert len(c3) == 1
        assert c3[0]['drug_index'] == three_drugs[2].id - 1


class TestPrepareCombinationContext:

    def test_empty(self, calculator_base):
        ctx = calculator_base._prepare_combination_context([], [])
        assert ctx['combinations'][0]['drugs'] == []
        assert ctx['combinations'][1]['drugs'] == []


class TestAnalyzeMaxDrugContribution:

    def test_no_effects(self, calculator_base):
        recs = calculator_base._analyze_max_drug_contribution(
            [], np.array([]), [], np.array([]), {}
        )
        assert recs == {'rep_recommendations': []}