"""Валидация входных данных CalculationAPI."""
import re
from unittest.mock import MagicMock, patch

import pytest
from rest_framework import status

from drugs.utils.custom_response import CustomResponse
from drugs.models import Drug
from side_effects.models import DrugSideEffect, SideEffect
from ranker.views import CalculationAPI


pytestmark = pytest.mark.django_db


class TestValidateInputData:

    def _call(self, data, files=None):
        request = MagicMock()
        request.data = data
        request.FILES = files or {}
        return CalculationAPI()._validate_input_data(request)

    def test_valid_drugs(self):
        assert self._call({"drugs": [1, 2]}) == ([1, 2], None, None)

    def test_drugs_as_json_string(self):
        assert self._call({"drugs": "[1, 2, 3]"}) == ([1, 2, 3], None, None)

    def test_missing_drugs(self):
        result = self._call({})
        assert isinstance(result, CustomResponse)
        assert result.status_code == 400

    def test_invalid_drugs_json(self):
        result = self._call({"drugs": "not-json"})
        assert isinstance(result, CustomResponse)
        assert result.status_code == 400

    def test_human_data_as_json_string(self):
        assert self._call({"drugs": [1, 2], "humanData": '{"age": 30}'}) == \
            ([1, 2], {"age": 30}, None)

    def test_human_data_invalid_json(self):
        result = self._call({"drugs": [1, 2], "humanData": "not-json"})
        assert isinstance(result, CustomResponse)
        assert result.status_code == 400

    def test_med_card_from_files(self):
        med = object()
        assert self._call({"drugs": [1, 2]}, files={"medCard": med}) == \
            ([1, 2], None, med)


# ---- сюда перенести всё из test_validate_input_data.py ----

class TestValidateWeightsCompletenessMocked:

    @pytest.fixture
    def api_instance(self):
        return CalculationAPI()

    @patch('ranker.views.SideEffect')
    @patch('ranker.views.Drug')
    @patch('ranker.views.DrugSideEffect')
    def test_no_side_effects_returns_error(self, mock_dse, mock_drug, mock_se, api_instance):
        mock_se.objects.count.return_value = 0
        result = api_instance._validate_weights_completeness()
        assert isinstance(result, CustomResponse)
        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert "не загружены" in result.data['result']['message']

    @patch('ranker.views.SideEffect')
    @patch('ranker.views.Drug')
    @patch('ranker.views.DrugSideEffect')
    def test_mismatch_returns_error(self, mock_dse, mock_drug, mock_se, api_instance):
        mock_se.objects.count.return_value = 10
        mock_drug.objects.count.return_value = 5
        mock_dse.objects.count.return_value = 40
        result = api_instance._validate_weights_completeness()
        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert "50" in result.data['result']['message']
        assert "40" in result.data['result']['message']

    @patch('ranker.views.SideEffect')
    @patch('ranker.views.Drug')
    @patch('ranker.views.DrugSideEffect')
    def test_valid_returns_none(self, mock_dse, mock_drug, mock_se, api_instance):
        mock_se.objects.count.return_value = 10
        mock_drug.objects.count.return_value = 5
        mock_dse.objects.count.return_value = 50
        assert api_instance._validate_weights_completeness() is None


class TestValidateWeightsCompletenessRealDB:

    @pytest.fixture
    def api_instance(self):
        return CalculationAPI()

    @pytest.fixture
    def setup_test_data(self):
        se1 = SideEffect.objects.create(se_name="Головная боль", weight=0.5)
        se2 = SideEffect.objects.create(se_name="Тошнота", weight=0.3)
        d1 = Drug.objects.create(drug_name="Аспирин")
        d2 = Drug.objects.create(drug_name="Парацетамол")
        return {'se': [se1, se2], 'drugs': [d1, d2]}

    def test_valid_with_real_data(self, api_instance, setup_test_data):
        for drug in setup_test_data['drugs']:
            for se in setup_test_data['se']:
                DrugSideEffect.objects.create(
                    drug=drug, side_effect=se, probability=0.1,
                    rang_base=0.5, rang_f1=0.6, rang_f2=0.7,
                    rang_freq=0.8, rang_m1=0.9, rang_m2=1.0,
                )
        assert api_instance._validate_weights_completeness() is None

    def test_mismatch_with_real_data(self, api_instance, setup_test_data):
        drug1, drug2 = setup_test_data['drugs']
        se1, se2 = setup_test_data['se']
        DrugSideEffect.objects.create(drug=drug1, side_effect=se1, probability=0.1)
        DrugSideEffect.objects.create(drug=drug1, side_effect=se2, probability=0.2)
        DrugSideEffect.objects.create(drug=drug2, side_effect=se1, probability=0.1)

        result = api_instance._validate_weights_completeness()
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        message = result.data['result']['message']
        match = re.search(r'ожидается (\d+) .* найдено (\d+)', message)
        assert match is not None
        expected, actual = map(int, match.groups())
        assert expected == 4 and actual == 3