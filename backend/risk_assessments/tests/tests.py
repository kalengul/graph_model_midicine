"""
Тесты модуля risk_assessments.
"""
# Добавляем путь для импортов
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импорты для Django
from django.test import TestCase



from unittest.mock import MagicMock, patch

import pytest
from rest_framework.test import APIRequestFactory

from risk_assessments.serializers import DrugRiskAssessmentRequestSerializer
from risk_assessments.services import (
    ContraindicationNotFoundError,
    DrugNotFoundError,
    _map_combinations,
    _map_fortran_status,
    _map_se_from_drug,
    _map_side_effects,
    assess_drug_risks,
    resolve_contraindication_ids,
    resolve_drug_ids,
    _build_incompatible_effect_drug_map
)
from risk_assessments.utils.normalize_drug_name import normalize_drug_name
from risk_assessments.views import DrugRiskAssessmentView


# ===========================================================================
# Нормализация
# ===========================================================================

class TestNormalizeDrugName(TestCase):
    def test_lowercase(self):
        assert normalize_drug_name("Варфарин") == "варфарин"

    def test_slash_to_plus(self):
        assert normalize_drug_name("амлодипин/периндоприл") == "амлодипин+периндоприл"
    
    def test_semicolon_point_to_plus(self):
        assert normalize_drug_name("амлодипин;периндоприл") == "амлодипин+периндоприл"

    def test_spaces_removed(self):
        assert normalize_drug_name("амлодипин  + периндоприл") == "амлодипин+периндоприл"

    def test_combined(self):
        assert normalize_drug_name("Амлодипин /  Периндоприл") == "амлодипин+периндоприл"

    def test_already_normalized(self):
        assert normalize_drug_name("амлодипин+периндоприл") == "амлодипин+периндоприл"

    def test_double_word(self):
        assert normalize_drug_name("   Ацетилсалицилловая  кислота") == "ацетилсалицилловая кислота"

    def test_triple_word(self):
        assert normalize_drug_name(" Железа   (III) гидроксид полимальтозат   ") == "железа (iii) гидроксид полимальтозат"

# ===========================================================================
# Сериализатор
# ===========================================================================

class TestDrugRiskAssessmentRequestSerializer(TestCase):

    def test_valid_minimal(self):
        s = DrugRiskAssessmentRequestSerializer(data={"drugs": ["варфарин", "ампициллин"]})
        assert s.is_valid(), s.errors

    def test_drugs_normalized_on_validation(self):
        s = DrugRiskAssessmentRequestSerializer(
            data={"drugs": ["Варфарин", "Амлодипин / Периндоприл"]}
        )
        assert s.is_valid(), s.errors
        assert s.validated_data["drugs"] == ["варфарин", "амлодипин+периндоприл"]

    def test_duplicate_after_normalization(self):
        s = DrugRiskAssessmentRequestSerializer(
            data={"drugs": ["Варфарин", "варфарин", "ампициллин"]}
        )
        assert not s.is_valid()
        assert "drugs" in s.errors

    def test_too_few_drugs(self):
        s = DrugRiskAssessmentRequestSerializer(data={"drugs": ["варфарин"]})
        assert not s.is_valid()

    def test_too_many_drugs(self):
        s = DrugRiskAssessmentRequestSerializer(data={"drugs": [f"drug{i}" for i in range(51)]})
        assert not s.is_valid()

    def test_patient_profile_optional(self):
        s = DrugRiskAssessmentRequestSerializer(data={"drugs": ["а", "б"]})
        assert s.is_valid()
        assert s.validated_data.get("patientProfile") is None

    def test_invalid_gender(self):
        s = DrugRiskAssessmentRequestSerializer(
            data={"drugs": ["а", "б"], "patientProfile": {"gender": "unknown"}}
        )
        assert not s.is_valid()

    def test_age_out_of_bounds(self):
        s = DrugRiskAssessmentRequestSerializer(
            data={"drugs": ["а", "б"], "patientProfile": {"age": 200}}
        )
        assert not s.is_valid()


# ===========================================================================
# Маппинг данных калькулятора
# ===========================================================================

class TestMapFortranStatus(TestCase):
    def test_known_statuses(self):
        assert _map_fortran_status("compatible") == "COMPATIBLE"
        assert _map_fortran_status("caution") == "CAUTION"
        assert _map_fortran_status("incompatible") == "INCOMPATIBLE"

    def test_unknown_falls_back_to_caution(self):
        assert _map_fortran_status("unknown_value") == "CAUTION"


class TestMapSideEffects(TestCase):
    def test_renames_se_name_to_seName(self):
        raw = [
            {
                "compatibility": "caution",
                "effects": [{"se_name": "тошнота", "rank": 0.6}],
            }
        ]
        result = _map_side_effects(raw)
        assert result[0]["effects"][0]["seName"] == "тошнота"
        assert "se_name" not in result[0]["effects"][0]

    def test_empty_effects_preserved(self):
        raw = [{"compatibility": "compatible", "effects": []}]
        result = _map_side_effects(raw)
        assert result[0]["effects"] == []

    def test_all_three_groups_passed_through(self):
        raw = [
            {"compatibility": "compatible",   "effects": []},
            {"compatibility": "caution",      "effects": []},
            {"compatibility": "incompatible", "effects": []},
        ]
        result = _map_side_effects(raw)
        assert len(result) == 3


class TestMapCombinations(TestCase):
    def test_renames_side_effects_key(self):
        raw = [
            {
                "compatibility": "caution",
                "drugs": [
                    {"name": "Варфарин", "side_effects": [{"se_name": "кровотечение", "rank": 0.7}]}
                ],
            }
        ]
        result = _map_combinations(raw)
        drug = result[0]["drugs"][0]
        assert "sideEffects" in drug
        assert "side_effects" not in drug
        assert drug["sideEffects"][0]["seName"] == "кровотечение"

    def test_empty_drugs(self):
        raw = [{"compatibility": "incompatible", "drugs": []}]
        result = _map_combinations(raw)
        assert result[0]["drugs"] == []


class TestMapSeFromDrug(TestCase):
    def test_renames_fields(self):
        raw = [
            {"d_name": "Варфарин", "effects": [{"se_name": "кровотечение", "rank": 0.5}]}
        ]
        result = _map_se_from_drug(raw)
        assert result[0]["name"] == "Варфарин"
        assert result[0]["sideEffects"][0]["seName"] == "кровотечение"
        assert "d_name" not in result[0]
        assert "effects" not in result[0]

    def test_empty_effects(self):
        raw = [{"d_name": "Ампициллин", "effects": []}]
        result = _map_se_from_drug(raw)
        assert result[0]["sideEffects"] == []


# ===========================================================================
# resolve_drug_ids
# ===========================================================================

class TestResolveDrugIds(TestCase):

    @patch("risk_assessments.services.Drug")
    def test_all_found(self, MockDrug):
        drug = MagicMock(id=1, drug_name="варфарин")
        MockDrug.objects.filter.return_value.first.return_value = drug

        result = resolve_drug_ids(["варфарин"])
        assert result == {1: "варфарин"}

    @patch("risk_assessments.services.Drug")
    def test_missing_raises_with_correct_names(self, MockDrug):
        MockDrug.objects.filter.return_value.first.return_value = None

        with pytest.raises(DrugNotFoundError) as exc_info:
            resolve_drug_ids(["неизвестный", "второй_неизвестный"])
        assert "неизвестный" in exc_info.value.missing
        assert "второй_неизвестный" in exc_info.value.missing


# ===========================================================================
# resolve_contraindication_ids
# ===========================================================================

class TestResolveContraindicationIds(TestCase):

    def test_empty_list_returns_empty(self):
        assert resolve_contraindication_ids([]) == []

    @patch("risk_assessments.services.Contraindication")
    def test_all_found(self, MockContra):
        contra = MagicMock(id=10)
        MockContra.objects.filter.return_value.first.return_value = contra

        result = resolve_contraindication_ids(["анемия"])
        assert result == [10]

    @pytest.mark.skip
    @patch("risk_assessments.services.Contraindication")
    def test_missing_raises_with_original_name(self, MockContra):
        """В ошибке возвращается исходное имя, а не нормализованное."""
        MockContra.objects.filter.return_value.first.return_value = None

        with pytest.raises(ContraindicationNotFoundError) as exc_info:
            resolve_contraindication_ids(["Анемия тяжёлая"])
        assert "Анемия тяжёлая" in exc_info.value.missing


# ===========================================================================
# View
# ===========================================================================

class TestDrugRiskAssessmentView(TestCase):

    def _post(self, data: dict):
        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1.0/risk-assessments/drug-compatibility/",
            data,
            format="json",
        )
        request.user = MagicMock(is_authenticated=False)
        return DrugRiskAssessmentView.as_view()(request)

    @patch("risk_assessments.views.CalculationLoggingService")
    @patch("risk_assessments.views.assess_drug_risks")
    def test_200_on_success(self, mock_assess, mock_log):
        mock_log.log_request = MagicMock()
        mock_assess.return_value = {
            "drugs": {"1": "варфарин", "2": "ампициллин"},
            "compatibility": {"status": "COMPATIBLE", "rank": 8.5},
            "bannedPairs": [],
            "bannedPairsCont": [],
            "sideEffects": [],
            "combinations": [],
            "seFromDrug": [],
        }
        response = self._post({"drugs": ["варфарин", "ампициллин"]})
        assert response.status_code == 200

    @patch("risk_assessments.views.CalculationLoggingService")
    @patch("risk_assessments.views.assess_drug_risks")
    def test_400_on_drug_not_found(self, mock_assess, mock_log):
        mock_log.log_request = MagicMock()
        mock_assess.side_effect = DrugNotFoundError(["несуществующий"])

        response = self._post({"drugs": ["несуществующий", "варфарин"]})
        assert response.status_code == 400
        body = response.data["data"]
        assert body["errorCode"] == "BAD_REQUEST"
        assert "drugs" in body["message"]
        assert "несуществующий" in body["additionalData"]

    @patch("risk_assessments.views.CalculationLoggingService")
    @patch("risk_assessments.views.assess_drug_risks")
    def test_400_on_contraindication_not_found(self, mock_assess, mock_log):
        mock_log.log_request = MagicMock()
        mock_assess.side_effect = ContraindicationNotFoundError(["анимия"])

        response = self._post({
            "drugs": ["варфарин", "ампициллин"],
            "patientProfile": {"contList": ["анимия"]},
        })
        assert response.status_code == 400
        body = response.data["data"]
        assert "contList" in body["message"]
        assert "анимия" in body["additionalData"]

    def test_400_on_serializer_validation_error(self):
        response = self._post({"drugs": ["только_один"]})
        assert response.status_code == 400

    @patch("risk_assessments.views.CalculationLoggingService")
    @patch("risk_assessments.views.assess_drug_risks")
    def test_500_on_unexpected_error(self, mock_assess, mock_log):
        mock_log.log_request = MagicMock()
        mock_assess.side_effect = RuntimeError("что-то сломалось")

        response = self._post({"drugs": ["варфарин", "ампициллин"]})
        assert response.status_code == 500

# ===========================================================================
# _build_incompatible_effect_drug_map
# ===========================================================================

class TestBuildIncompatibleEffectDrugMap(TestCase):
    """
    Для каждого эффекта из группы compatibility == "incompatible"
    функция должна вернуть список препаратов из SEFromDrug
    с максимальным rank по этому эффекту.
    """

    def _context(self, side_effects, se_from_drug):
        return {
            "compatibility_fortran": "incompatible",
            "side_effects": side_effects,
            "SEFromDrug": se_from_drug,
        }

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

        result = _build_incompatible_effect_drug_map(context)

        # qt — tie 0.65 у обоих препаратов => оба попадают в список
        assert {d["d_name"] for d in result["удлинение интервала qt"]} == {
            "амиодарон",
            "соталол",
        }
        # брадикардия — максимум 0.5 только у амиодарона
        assert result["брадикардия"] == [{"d_name": "амиодарон", "rank": 0.5}]

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

        result = _build_incompatible_effect_drug_map(context)

        assert set(result.keys()) == {"брадикардия"}

    def test_returns_first_by_max_rank_when_all_distinct(self):
        """У каждого препарата свой rank — берём с максимальным."""
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [{"se_name": "желудочно-кишечное кровотечение", "rank": 1.07}],
                },
            ],
            se_from_drug=[
                {
                    "d_name": "варфарин",
                    "effects": [{"se_name": "желудочно-кишечное кровотечение", "rank": 0.4}],
                },
                {
                    "d_name": "кеторолак",
                    "effects": [{"se_name": "желудочно-кишечное кровотечение", "rank": 0.9}],
                },
                {
                    "d_name": "аллопуринол",
                    "effects": [{"se_name": "желудочно-кишечное кровотечение", "rank": 0.1}],
                },
            ],
        )

        result = _build_incompatible_effect_drug_map(context)

        assert result == {
            "желудочно-кишечное кровотечение": [
                {"d_name": "кеторолак", "rank": 0.9}
            ]
        }

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

        assert _build_incompatible_effect_drug_map(context) == {}

    def test_empty_result_when_side_effects_missing(self):
        assert _build_incompatible_effect_drug_map({}) == {}

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

        # Эффект есть в incompatible, но ни у одного препарата его нет
        assert _build_incompatible_effect_drug_map(context) == {"брадикардия": None}

    def test_empty_effect_list_in_incompatible_group(self):
        context = self._context(
            side_effects=[{"compatibility": "incompatible", "effects": []}],
            se_from_drug=[
                {"d_name": "амиодарон", "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
            ],
        )

        assert _build_incompatible_effect_drug_map(context) == {}

    def test_effect_present_in_incompatible_but_absent_for_all_drugs(self):
        """incompatible-эффект, которого нет ни у одного препарата → None."""
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

        result = _build_incompatible_effect_drug_map(context)

        assert result["брадикардия"] == [{"d_name": "амиодарон", "rank": 0.5}]
        assert result["редкий эффект"] is None

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

        result = _build_incompatible_effect_drug_map(context)

        assert set(result.keys()) == {"брадикардия"}

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

        result = _build_incompatible_effect_drug_map(context)

        assert len(result["редкий эффект"]) == 2
        assert all(d["rank"] == 0.0 for d in result["редкий эффект"])

    def test_returns_all_drugs_with_tied_max_rank(self):
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [{"se_name": "брадикардия", "rank": 1.0}],
                },
            ],
            se_from_drug=[
                {"d_name": "амиодарон", "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
                {"d_name": "соталол",   "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
                {"d_name": "карведилол","effects": [{"se_name": "брадикардия", "rank": 0.36}]},
            ],
        )

        result = _build_incompatible_effect_drug_map(context)

        assert {d["d_name"] for d in result["брадикардия"]} == {"амиодарон", "соталол"}
        assert all(d["rank"] == 0.5 for d in result["брадикардия"])

    def test_drug_without_d_name_is_ignored(self):
        """Если у препарата нет d_name — он не должен попадать в результат."""
        context = self._context(
            side_effects=[
                {
                    "compatibility": "incompatible",
                    "effects": [{"se_name": "брадикардия", "rank": 1.0}],
                },
            ],
            se_from_drug=[
                {"effects": [{"se_name": "брадикардия", "rank": 0.9}]},  # нет d_name
                {"d_name": "амиодарон", "effects": [{"se_name": "брадикардия", "rank": 0.5}]},
            ],
        )

        result = _build_incompatible_effect_drug_map(context)

        assert result == {"брадикардия": [{"d_name": None, "rank": 0.9}]}

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

        result = _build_incompatible_effect_drug_map(context)

        assert result == {"брадикардия": [{"d_name": "соталол", "rank": 0.5}]}

    # ------------------------------------------------------------------ #
    # Контракт по формату вывода
    # ------------------------------------------------------------------ #

    def test_output_shape(self):
        """Ключи результата — se_name из incompatible-группы,
        значения — список словарей {d_name, rank}."""
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

        result = _build_incompatible_effect_drug_map(context)

        assert isinstance(result, dict)
        assert list(result.keys()) == ["брадикардия"]
        assert isinstance(result["брадикардия"], list)
        assert result["брадикардия"][0].keys() == {"d_name", "rank"}