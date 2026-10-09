"""Тесты CalculationAPI.post."""
from unittest.mock import patch

import pytest

from drugs.utils.custom_response import CustomResponse
from ranker.views import CalculationAPI


pytestmark = pytest.mark.django_db


class TestCalculationAPIPost:

    def _call(self, factory, data=None):
        request = factory.post(
            "/api/v1/polifarmakoterapiya-fortran/",
            data or {},
            format="json",
        )
        return CalculationAPI.as_view()(request)

    @patch("ranker.views.FortranLog.log_request")
    @patch.object(CalculationAPI, "_calculate_compatibility")
    @patch.object(CalculationAPI, "_create_base_response_template")
    @patch.object(CalculationAPI, "_validate_input_data")
    def test_validation_error(self, mock_validate, mock_template,
                              mock_calc, mock_log, factory):
        mock_validate.return_value = CustomResponse(
            status=400, message="bad", http_status=400
        )
        response = self._call(factory)
        assert response.status_code == 400
        mock_template.assert_not_called()
        mock_calc.assert_not_called()
        assert mock_log.call_args.kwargs.get("status") == "error"

    @patch("ranker.views.FortranLog.log_request")
    @patch("ranker.views.DrugPairChecker")
    @patch.object(CalculationAPI, "_create_base_response_template")
    @patch.object(CalculationAPI, "_validate_input_data")
    def test_banned(self, mock_validate, mock_template, MockChecker,
                    mock_log, factory):
        mock_validate.return_value = ([1, 2], None, None)
        mock_template.return_value = {"drugs": ["A", "B"]}
        MockChecker.return_value.check_banned.return_value = [
            {"pair": ["A", "B"], "comment": "x"}
        ]
        response = self._call(factory)
        assert response.status_code == 200
        assert mock_log.call_args.kwargs.get("status") == CalculationAPI.COMPATIBILITY_BANNED

    @patch("ranker.views.FortranLog.log_request")
    @patch("ranker.views.DrugPairChecker")
    @patch.object(CalculationAPI, "_exist_contraindications")
    @patch.object(CalculationAPI, "_create_base_response_template")
    @patch.object(CalculationAPI, "_validate_input_data")
    def test_contraindications(self, mock_validate, mock_template,
                               mock_exist, MockChecker, mock_log, factory):
        mock_validate.return_value = ([1, 2], {"cont_list": [10]}, None)
        mock_template.return_value = {"drugs": ["A", "B"]}
        MockChecker.return_value.check_banned.return_value = []
        mock_exist.return_value = [("A", ["язва"])]
        response = self._call(factory)
        assert response.status_code == 200
        assert mock_log.call_args.kwargs.get("status") == \
            CalculationAPI.COMPATIBILITY_BANNED_CONTRAINDICATIONS
        assert mock_log.call_args.kwargs.get("banned_pairs_cont") == [("A", ["язва"])]

    @patch("ranker.views.FortranLog.log_request")
    @patch("ranker.views.DrugPairChecker")
    @patch.object(CalculationAPI, "_calculate_compatibility")
    @patch.object(CalculationAPI, "_create_base_response_template")
    @patch.object(CalculationAPI, "_validate_input_data")
    def test_success(self, mock_validate, mock_template, mock_calc,
                     MockChecker, mock_log, factory):
        mock_validate.return_value = ([1, 2], None, None)
        mock_template.return_value = {"drugs": ["A", "B"]}
        MockChecker.return_value.check_banned.return_value = []
        mock_calc.return_value = {
            "compatibility_fortran": "caution", "rank_iteractions": 0.5,
        }
        response = self._call(factory)
        assert response.status_code == 200
        assert mock_log.call_args.kwargs.get("status") == "caution"
        assert mock_log.call_args.kwargs.get("rank") == 0.5

    @patch("ranker.views.FortranLog.log_request")
    @patch("ranker.views.DrugPairChecker")
    @patch.object(CalculationAPI, "_calculate_compatibility")
    @patch.object(CalculationAPI, "_create_base_response_template")
    @patch.object(CalculationAPI, "_validate_input_data")
    def test_calc_returns_custom_response(self, mock_validate, mock_template,
                                          mock_calc, MockChecker, mock_log,
                                          factory):
        mock_validate.return_value = ([1, 2], None, None)
        mock_template.return_value = {"drugs": ["A", "B"]}
        MockChecker.return_value.check_banned.return_value = []
        mock_calc.return_value = CustomResponse(
            status=400, message="weights", http_status=400
        )
        response = self._call(factory)
        assert response.status_code == 400
        assert mock_log.call_args.kwargs.get("status") == "error"

    @patch("ranker.views.FortranLog.log_request")
    @patch.object(CalculationAPI, "_validate_input_data")
    def test_exception(self, mock_validate, mock_log, factory):
        mock_validate.side_effect = RuntimeError("boom")
        response = self._call(factory)
        assert response.status_code == 500
        assert mock_log.call_args.kwargs.get("status") == "error"