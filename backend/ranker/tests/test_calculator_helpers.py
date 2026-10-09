"""Вспомогательные методы FortranCalculator."""
import pytest

from drugs.models import Drug, DrugGroup
from side_effects.models import SideEffect, SideEffectsGender


pytestmark = pytest.mark.django_db


class TestValidateCancelingGroups:

    def test_valid(self, calculator_base):
        assert calculator_base._validate_canceling_groups([[1, 2], [2, 3, 1]]) == \
            [[1, 2], [2, 3, 1]]

    def test_invalid_filtered_out(self, calculator_base):
        assert calculator_base._validate_canceling_groups(
            [[1], [2, 100], "not list", [1, 2, 3]]
        ) == [[1, 2, 3]]

    def test_none(self, calculator_base):
        assert calculator_base._validate_canceling_groups(None) is None

    def test_not_list(self, calculator_base):
        assert calculator_base._validate_canceling_groups("not_list") is None


class TestGetExcludedSeByGender:

    def test_man_and_woman(self, calculator_base, three_side_effects):
        se1 = SideEffect.objects.get(se_name="внутричерепное кровоизлияние")
        se2 = SideEffect.objects.get(se_name="гипокалиемия")
        se3 = SideEffect.objects.get(se_name="гиперкалиемия")
        SideEffectsGender.objects.get_or_create(side_effect=se1, gender='man')
        SideEffectsGender.objects.get_or_create(side_effect=se2, gender='woman')
        SideEffectsGender.objects.get_or_create(side_effect=se3, gender='man')

        assert calculator_base._get_excluded_se_by_gender('man') == {se2.id}
        assert calculator_base._get_excluded_se_by_gender('woman') == {se1.id, se3.id}

    def test_none(self, calculator_base):
        assert calculator_base._get_excluded_se_by_gender(None) == set()


class TestLoadSideEffectsDict:

    def test_with_excluded(self, calculator_base, three_side_effects):
        excluded = {SideEffect.objects.get(se_name="гипокалиемия").id}
        id2side = calculator_base._load_side_effects_dict(excluded)
        expected = {
            se.id - 1: se.se_name
            for se in three_side_effects
            if se.id not in excluded
        }
        assert id2side == expected


class TestGetExcludedDrugsByGroups:

    @pytest.mark.django_db(transaction=True)
    def test_same_group_excluded(self, calculator_base):
        DrugGroup.objects.all().delete()
        Drug.objects.all().delete()
        group = DrugGroup.objects.create(dg_name="Тестовая группа")
        d1 = Drug.objects.create(drug_name="Тест1")
        d2 = Drug.objects.create(drug_name="Тест2")
        Drug.objects.create(drug_name="Тест3")
        d1.drug_groups.add(group)
        d2.drug_groups.add(group)

        assert calculator_base._get_excluded_drugs_by_groups([d1.id]) == {d2.id - 1}

    def test_empty_input(self, calculator_base):
        assert calculator_base._get_excluded_drugs_by_groups([]) == set()


class TestGetSeFromDrugs:

    def test_two_drugs(self, calculator_base, filled_db):
        three_drugs, _ = filled_db
        n_drug = [d.id for d in three_drugs[:2]]
        result = calculator_base._get_se_from_drugs(n_drug, set(), 'rang_base')
        assert len(result) == 2
        assert len(result[0]['effects']) == 3
        ranks = [e['rank'] for e in result[0]['effects']]
        assert sorted(ranks, reverse=True) == [0.3, 0.06, 0.0]

    def test_empty(self, calculator_base):
        assert calculator_base._get_se_from_drugs([], set(), 'rang_base') == []


class TestGetDrugNamesBulk:

    def test_two_names(self, calculator_base, filled_db):
        three_drugs, _ = filled_db
        ids = [d.id for d in three_drugs[:2]]
        names = calculator_base._get_drug_names_bulk(ids)
        assert len(names) == 2
        assert names[three_drugs[0].id] == three_drugs[0].drug_name

    def test_empty(self, calculator_base):
        assert calculator_base._get_drug_names_bulk([]) == {}