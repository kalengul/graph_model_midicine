"""Тесты для ranker.utils.check_banned.DrugPairChecker."""
import pytest

from drugs.models import BannedDrugPair, Drug
from ranker.utils.check_banned import DrugPairChecker


pytestmark = pytest.mark.django_db


class TestDrugPairChecker:

    @pytest.fixture
    def drugs(self):
        """Три препарата с фиксированными именами."""
        return {
            "a": Drug.objects.create(drug_name="Аспирин"),
            "b": Drug.objects.create(drug_name="Варфарин"),
            "c": Drug.objects.create(drug_name="Парацетамол"),
        }

    def test_empty_list(self):
        """Пустой список препаратов → пустой результат, без обращений к БД."""
        assert DrugPairChecker().check_banned([]) == []

    def test_single_drug(self):
        """Один препарат — combinations не даёт ни одной пары."""
        d = Drug.objects.create(drug_name="Аспирин")
        assert DrugPairChecker().check_banned([d.id]) == []

    def test_no_banned_pairs_registered(self, drugs):
        """Препараты есть, но в BannedDrugPair нет ни одной пары из них."""
        result = DrugPairChecker().check_banned(
            [drugs["a"].id, drugs["b"].id, drugs["c"].id]
        )
        assert result == []

    def test_pair_found_direct_order(self, drugs):
        """Пара записана в БД в прямом порядке — находится."""
        BannedDrugPair.objects.create(
            first_drug="Аспирин", second_drug="Варфарин", comment="кровотечение",
        )
        result = DrugPairChecker().check_banned([drugs["a"].id, drugs["b"].id])
        assert result == [
            {"pair": ["Аспирин", "Варфарин"], "comment": "кровотечение"}
        ]

    def test_pair_found_reverse_order(self, drugs):
        """Пара записана в обратном порядке — тоже находится (Q с двумя условиями)."""
        BannedDrugPair.objects.create(
            first_drug="Варфарин", second_drug="Аспирин", comment="кровотечение",
        )
        result = DrugPairChecker().check_banned([drugs["a"].id, drugs["b"].id])
        assert result == [
            {"pair": ["Аспирин", "Варфарин"], "comment": "кровотечение"}
        ]

    def test_case_insensitive(self, drugs):
        """Регистр в BannedDrugPair не важен (iexact)."""
        BannedDrugPair.objects.create(
            first_drug="аспирин", second_drug="ВАРФАРИН", comment="x",
        )
        result = DrugPairChecker().check_banned([drugs["a"].id, drugs["b"].id])
        assert result == [{"pair": ["Аспирин", "Варфарин"], "comment": "x"}]

    def test_multiple_pairs_preserve_combination_order(self, drugs):
        """Пары перебираются в порядке combinations(drugs, 2)."""
        BannedDrugPair.objects.create(
            first_drug="Аспирин", second_drug="Варфарин", comment="c1",
        )
        BannedDrugPair.objects.create(
            first_drug="Аспирин", second_drug="Парацетамол", comment="c2",
        )
        BannedDrugPair.objects.create(
            first_drug="Варфарин", second_drug="Парацетамол", comment="c3",
        )
        result = DrugPairChecker().check_banned(
            [drugs["a"].id, drugs["b"].id, drugs["c"].id]
        )
        assert result == [
            {"pair": ["Аспирин", "Варфарин"], "comment": "c1"},
            {"pair": ["Аспирин", "Парацетамол"], "comment": "c2"},
            {"pair": ["Варфарин", "Парацетамол"], "comment": "c3"},
        ]

    def test_only_registered_pair_is_returned(self, drugs):
        """Из трёх комбинаций только одна запрещена — возвращается только она."""
        BannedDrugPair.objects.create(
            first_drug="Аспирин", second_drug="Варфарин", comment="c",
        )
        result = DrugPairChecker().check_banned(
            [drugs["a"].id, drugs["b"].id, drugs["c"].id]
        )
        assert result == [{"pair": ["Аспирин", "Варфарин"], "comment": "c"}]

    def test_none_comment_kept_as_none(self, drugs):
        """Комментарий может быть NULL — попадает в результат как None."""
        BannedDrugPair.objects.create(
            first_drug="Аспирин", second_drug="Варфарин", comment=None,
        )
        result = DrugPairChecker().check_banned([drugs["a"].id, drugs["b"].id])
        assert result == [{"pair": ["Аспирин", "Варфарин"], "comment": None}]

    def test_unknown_drug_id_raises_keyerror(self):
        """
        Если в drugs передан несуществующий id, drug_map его не содержит
        и код падает на drug_map[id1].drug_name.

        Фиксируем текущее поведение — это не баг теста, а контракт метода.
        """
        d = Drug.objects.create(drug_name="Аспирин")
        with pytest.raises(KeyError):
            DrugPairChecker().check_banned([d.id, 999999])

    def test_order_of_names_in_result_follows_input_order(self, drugs):
        """
        Даже если в BannedDrugPair пара лежит как (Варфарин, Аспирин),
        в результате имена идут в порядке их появления в списке drugs.
        """
        BannedDrugPair.objects.create(
            first_drug="Варфарин", second_drug="Аспирин", comment="c",
        )
        # Явно передаём varfarin первым
        result = DrugPairChecker().check_banned([drugs["b"].id, drugs["a"].id])
        assert result == [{"pair": ["Варфарин", "Аспирин"], "comment": "c"}]