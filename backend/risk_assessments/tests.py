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
)
from risk_assessments.utils import normalize_drug_name
from risk_assessments.views import DrugRiskAssessmentView


# ===========================================================================
# Нормализация
# ===========================================================================

class TestNormalizeDrugName(TestCase):
    def test_lowercase(self):
        assert normalize_drug_name("Варфарин") == "варфарин"

    def test_slash_to_plus(self):
        assert normalize_drug_name("амлодипин/периндоприл") == "амлодипин+периндоприл"

    def test_spaces_removed(self):
        assert normalize_drug_name("амлодипин + периндоприл") == "амлодипин+периндоприл"

    def test_combined(self):
        assert normalize_drug_name("Амлодипин / Периндоприл") == "амлодипин+периндоприл"

    def test_already_normalized(self):
        assert normalize_drug_name("амлодипин+периндоприл") == "амлодипин+периндоприл"


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