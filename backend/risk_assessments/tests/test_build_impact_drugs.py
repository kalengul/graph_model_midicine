# Добавляем путь для импортов
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импорты для Django
from django.test import TestCase

from risk_assessments.services import _build_max_impact_drugs

# ===========================================================================
# _build_max_impact_drugs
# ===========================================================================

class TestBuildMaxImpactDrugs(TestCase):
    """
    Для каждого эффекта из группы compatibility == "incompatible"
    функция возвращает ПЛОСКИЙ список записей:
        {"sideEffect": ..., "drugName": ..., "rank": ...}

    В список попадают препараты с максимальным rank по этому эффекту.
    Если для эффекта нет данных в SEFromDrug — эффект пропускается
    (никаких None-значений в результате).
    """

    def _context(self, side_effects, se_from_drug):
        return {
            "compatibility_fortran": "incompatible",
            "side_effects": side_effects,
            "SEFromDrug": se_from_drug,
        }

    def _by_effect(self, result: list, effect_name: str) -> list:
        """Хелпер: выбрать из плоского списка все строки по конкретному эффекту."""
        return [row for row in result if row["sideEffect"] == effect_name]

    # ------------------------------------------------------------------ #
    # Базовые случаи
    # ------------------------------------------------------------------ #

    def test_picks_drug_with_max_rank(self):
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [
                        {"se_name": "удлинение интервала qt", "rank": 1.3},
                        {"se_name": "брадикардия", "rank": 1.01},
                    ],
                },
            ],
            se_from_drug=[
                {
                    "d_name": "амиодарон",
                    "effects": [
                        {"se_name": "удлинение интервала qt", "rank": 0.65},
                        {"se_name": "брадикардия", "rank": 0.5},
                    ],
                },
                {
                    "d_name": "соталол",
                    "effects": [
                        {"se_name": "удлинение интервала qt", "rank": 0.65},
                        {"se_name": "брадикардия", "rank": 0.36},
                    ],
                },
            ],
        )

        result = _build_max_impact_drugs(context)

        # qt — tie 0.65 у обоих препаратов => обе строки в результате
        qt_rows = self._by_effect(result, "удлинение интервала qt")
        assert {r["drugName"] for r in qt_rows} == {"амиодарон", "соталол"}
        assert all(r["rank"] == 0.65 for r in qt_rows)

        # брадикардия — максимум 0.5 только у амиодарона
        brady_rows = self._by_effect(result, "брадикардия")
        assert brady_rows == [
            {"sideEffect": "брадикардия", "drugName": "амиодарон", "rank": 0.5}
        ]

    def test_only_incompatible_group_is_considered(self):
        """Эффекты из compatible / caution игнорируются."""
        context = self._context(
            side_effects=[
                {
                    "compatibility": "compatible",
                    "effects": [{"se_name": "тошнота", "rank": 0.9}],
                },
                {
                    "compatibility": "caution",
                    "effects": [{"se_name": "гипотензия", "rank": 0.8}],
                },
                {
                    "compatibility": "incompatible",
                    "effects": [{"se_name": "брадикардия", "rank": 1.0}],
                },
            ],
            se_from_drug=[
                {
                    "d_name": "амиодарон",
                    "effects": [
                        {"se_name": "тошнота", "rank": 0.1},
                        {"se_name": "гипотензия", "rank": 0.2},
                        {"se_name": "брадикардия", "rank": 0.5},
                    ],
                },
            ],
        )

        result = _build_max_impact_drugs(context)

        assert len(result) == 1
        assert result[0]["sideEffect"] == "брадикардия"
        assert {row["sideEffect"] for row in result} == {"брадикардия"}

    def test_returns_first_by_max_rank_when_all_distinct(self):
        """У каждого препарата свой rank — попадает только максимальный."""
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [
                        {"se_name": "желудочно-кишечное кровотечение", "rank": 1.07}
                    ],
                },
            ],
            se_from_drug=[
                {
                    "d_name": "варфарин",
                    "effects": [
                        {"se_name": "желудочно-кишечное кровотечение", "rank": 0.4}
                    ],
                },
                {
                    "d_name": "кеторолак",
                    "effects": [
                        {"se_name": "желудочно-кишечное кровотечение", "rank": 0.9}
                    ],
                },
                {
                    "d_name": "аллопуринол",
                    "effects": [
                        {"se_name": "желудочно-кишечное кровотечение", "rank": 0.1}
                    ],
                },
            ],
        )

        result = _build_max_impact_drugs(context)

        assert result == [
            {
                "sideEffect": "желудочно-кишечное кровотечение",
                "drugName": "кеторолак",
                "rank": 0.9,
            }
        ]

    # ------------------------------------------------------------------ #
    # Граничные случаи
    # ------------------------------------------------------------------ #

    def test_empty_result_when_no_incompatible_group(self):
        context = self._context(
            side_effects=[
                {"compatibility": "compatible", "effects": [{"se_name": "тошнота", "rank": 0.1}]},
                {"compatibility": "caution",    "effects": []},
            ],
            se_from_drug=[{"d_name": "амиодарон", "effects": []}],
        )

        assert _build_max_impact_drugs(context) == []

    def test_empty_result_when_side_effects_missing(self):
        assert _build_max_impact_drugs({}) == []

    def test_empty_result_when_se_from_drug_missing(self):
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [{"se_name": "брадикардия", "rank": 1.0}],
                },
            ],
            se_from_drug=[],
        )

        # Эффект есть в incompatible, но данных по препаратам нет → эффект пропускается
        assert _build_max_impact_drugs(context) == []

    def test_empty_effect_list_in_incompatible_group(self):
        context = self._context(
            side_effects=[{"compatibility": "incompatible", "effects": []}],
            se_from_drug=[
                {"d_name": "амиодарон", "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
            ],
        )

        assert _build_max_impact_drugs(context) == []

    def test_effect_present_in_incompatible_but_absent_for_all_drugs(self):
        """incompatible-эффект, которого нет ни у одного препарата, пропускается."""
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [
                        {"se_name": "брадикардия", "rank": 1.0},
                        {"se_name": "редкий эффект", "rank": 0.9},
                    ],
                },
            ],
            se_from_drug=[
                {"d_name": "амиодарон", "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
            ],
        )

        result = _build_max_impact_drugs(context)

        assert result == [
            {"sideEffect": "брадикардия", "drugName": "амиодарон", "rank": 0.5}
        ]
        # "редкий эффект" отсутствует в результате
        assert all(row["sideEffect"] != "редкий эффект" for row in result)

    def test_skips_effect_without_se_name(self):
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [
                        {"se_name": None, "rank": 1.0},
                        {"se_name": "брадикардия", "rank": 1.0},
                    ],
                },
            ],
            se_from_drug=[
                {"d_name": "амиодарон", "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
            ],
        )

        result = _build_max_impact_drugs(context)

        assert result == [
            {"sideEffect": "брадикардия", "drugName": "амиодарон", "rank": 0.5}
        ]

    def test_zero_rank_is_kept(self):
        """rank=0.0 — валидное значение, не должно теряться."""
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [{"se_name": "редкий эффект", "rank": 1.0}],
                },
            ],
            se_from_drug=[
                {"d_name": "амиодарон", "effects": [{"se_name": "редкий эффект", "rank": 0.0}]},
                {"d_name": "соталол",   "effects": [{"se_name": "редкий эффект", "rank": 0.0}]},
            ],
        )

        result = _build_max_impact_drugs(context)

        assert len(result) == 2
        assert all(row["sideEffect"] == "редкий эффект" for row in result)
        assert all(row["rank"] == 0.0 for row in result)

    def test_returns_all_drugs_with_tied_max_rank(self):
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [{"se_name": "брадикардия", "rank": 1.0}],
                },
            ],
            se_from_drug=[
                {"d_name": "амиодарон",  "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
                {"d_name": "соталол",    "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
                {"d_name": "карведилол", "effects": [{"se_name": "брадикардия", "rank": 0.36}]},
            ],
        )

        result = _build_max_impact_drugs(context)

        assert {row["drugName"] for row in result} == {"амиодарон", "соталол"}
        assert all(row["rank"] == 0.5 for row in result)
        assert all(row["sideEffect"] == "брадикардия" for row in result)

    def test_drug_without_d_name_is_returned_with_none(self):
        """
        Препарат без d_name сейчас НЕ отбрасывается: попадает в результат
        с drugName=None. Тест фиксирует текущее поведение.

        Если решите отбрасывать такие препараты в _build_max_impact_drugs,
        замените ассерт на:
            assert result == [
                {"sideEffect": "брадикардия", "drugName": "амиодарон", "rank": 0.5}
            ]
        """
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [{"se_name": "брадикардия", "rank": 1.0}],
                },
            ],
            se_from_drug=[
                {"effects": [{"se_name": "брадикардия", "rank": 0.9}]},   # нет d_name
                {"d_name": "амиодарон", "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
            ],
        )

        result = _build_max_impact_drugs(context)

        assert result == [
            {"sideEffect": "брадикардия", "drugName": None, "rank": 0.9},
        ]

    def test_drug_without_effects_key_is_ignored(self):
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [{"se_name": "брадикардия", "rank": 1.0}],
                },
            ],
            se_from_drug=[
                {"d_name": "амиодарон"},  # нет ключа effects
                {"d_name": "соталол", "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
            ],
        )

        result = _build_max_impact_drugs(context)

        assert result == [
            {"sideEffect": "брадикардия", "drugName": "соталол", "rank": 0.5}
        ]

    # ------------------------------------------------------------------ #
    # Контракт по формату вывода
    # ------------------------------------------------------------------ #

    def test_output_shape(self):
        """
        Результат — плоский список словарей с ключами
        {sideEffect, drugName, rank}.
        """
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [{"se_name": "брадикардия", "rank": 1.0}],
                },
            ],
            se_from_drug=[
                {"d_name": "амиодарон", "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
            ],
        )

        result = _build_max_impact_drugs(context)

        assert isinstance(result, list)
        assert len(result) == 1

        row = result[0]
        assert isinstance(row, dict)
        assert row.keys() == {"sideEffect", "drugName", "rank"}
        assert row["sideEffect"] == "брадикардия"
        assert row["drugName"] == "амиодарон"
        assert row["rank"] == 0.5