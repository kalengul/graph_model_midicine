"""Интеграционные тесты FortranCalculator.calculate."""
import numpy as np
import pytest

from drugs.models import DrugGroup
from side_effects.models import DrugSideEffect, SideEffect, SideEffectsGender
from ranker.utils.fortran_calculator import FortranCalculator


pytestmark = pytest.mark.django_db


class TestCalculate:

    def test_compatible(self, calculator_base):
        result = calculator_base.calculate('rang_base', [1, 2])
        assert result['compatibility_fortran'] == 'compatible'
        assert result['rank_iteractions'] == 0.35
        assert len(result['side_effects'][2]['effects']) == 0

    def test_caution(self, calculator_base, filled_db):
        three_drugs, three_side_effects = filled_db
        dse = DrugSideEffect.objects.get(
            drug=three_drugs[0], side_effect=three_side_effects[0]
        )
        original = dse.rang_base
        dse.rang_base = 0.6
        dse.save()
        try:
            result = calculator_base.calculate('rang_base', [three_drugs[0].id])
            assert result['compatibility_fortran'] == 'caution'
            assert result['rank_iteractions'] == 0.6
        finally:
            dse.rang_base = original
            dse.save()

    def test_incompatible(self, calculator_base, filled_db):
        three_drugs, _ = filled_db
        drug_amiodarone = three_drugs[0]
        effect_hyperkal = SideEffect.objects.get(se_name="гиперкалиемия")
        dse = DrugSideEffect.objects.get(
            drug=drug_amiodarone, side_effect=effect_hyperkal
        )
        original = dse.rang_base
        dse.rang_base = 1.2
        dse.save()
        try:
            result = calculator_base.calculate(
                'rang_base', [drug_amiodarone.id, three_drugs[2].id]
            )
            assert result['compatibility_fortran'] == 'incompatible'
        finally:
            dse.rang_base = original
            dse.save()

    def test_gender_exclusion(self, calculator_base, three_side_effects):
        se1 = SideEffect.objects.get(se_name="внутричерепное кровоизлияние")
        se2 = SideEffect.objects.get(se_name="гипокалиемия")
        se3 = SideEffect.objects.get(se_name="гиперкалиемия")

        SideEffectsGender.objects.get_or_create(side_effect=se1, gender='man')
        SideEffectsGender.objects.get_or_create(side_effect=se2, gender='woman')
        SideEffectsGender.objects.get_or_create(side_effect=se3, gender='man')

        result = calculator_base.calculate('rang_base', [1, 2], gender='man')
        assert result['compatibility_fortran'] == 'compatible'
        for se_list in result['side_effects']:
            for eff in se_list['effects']:
                assert eff['se_name'] != 'гипокалиемия'

    def test_with_canceling_normalization(self, calculator_with_canceling):
        result = calculator_with_canceling.calculate('rang_base', [1, 3])
        assert 'compatibility_fortran' in result

    @pytest.mark.django_db(transaction=True)
    def test_with_recommendations(self, filled_db):
        three_drugs, three_side_effects = filled_db
        drug_main, drug_alt = three_drugs[0], three_drugs[2]

        drug_main.drug_groups.clear()
        drug_alt.drug_groups.clear()
        group = DrugGroup.objects.create(dg_name="ТестоваяГруппа")
        drug_main.drug_groups.add(group)
        drug_alt.drug_groups.add(group)

        effect = three_side_effects[0]
        dse_main = DrugSideEffect.objects.get(drug=drug_main, side_effect=effect)
        dse_alt = DrugSideEffect.objects.get(drug=drug_alt, side_effect=effect)
        orig_main, orig_alt = dse_main.rang_base, dse_alt.rang_base

        dse_main.rang_base = 1.2
        dse_main.save()
        dse_alt.rang_base = 0.1
        dse_alt.save()
        try:
            calculator = FortranCalculator(
                normalize=False, cuttoff_not_life_threats_side_e=False
            )
            result = calculator.calculate('rang_base', [drug_main.id])

            assert result['compatibility_fortran'] == 'incompatible'
            recs = result['rep_recommendations']
            target = next((r for r in recs if r['group_name'] == group.dg_name), None)
            assert target is not None
            rec = target['drugs'][0]
            assert rec['drug_name'] == drug_main.drug_name
            assert drug_alt.drug_name in rec['replace_drugs']

            _, _, _ = calculator._build_rank_matrices([drug_main.id], 'rang_base')
        finally:
            dse_main.rang_base = orig_main
            dse_main.save()
            dse_alt.rang_base = orig_alt
            dse_alt.save()