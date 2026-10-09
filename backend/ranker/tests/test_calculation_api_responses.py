"""Формирование ответов CalculationAPI."""
from unittest.mock import MagicMock, patch

import pytest

from drugs.utils.custom_response import CustomResponse
from drugs.models import Drug
from ranker.views import CalculationAPI


pytestmark = pytest.mark.django_db


class TestCreateBaseResponseTemplate:

    def test_keys(self):
        d1 = Drug.objects.create(drug_name="Аспирин")
        d2 = Drug.objects.create(drug_name="Варфарин")
        result = CalculationAPI()._create_base_response_template([d1.id, d2.id])
        assert set(result.keys()) == {
            "side_effects", "SEFromDrug", "drugs",
            "compatibility_fortran", "bannedPairs", "bannedPairsCont",
        }
        assert sorted(result["drugs"]) == ["Аспирин", "Варфарин"]
        assert result["compatibility_fortran"] is None

    def test_empty(self):
        assert CalculationAPI()._create_base_response_template([])["drugs"] == []


class TestExistContraindications:

    @staticmethod
    def _make_drug(name="Аспирин", explicit=None, age_restrictions=None):
        drug = MagicMock()
        drug.drug_name = name
        intersect = MagicMock()
        intersect.exists.return_value = bool(explicit)
        intersect.values_list.return_value = explicit or []
        drug.contraindications.filter.return_value = intersect
        drug.age_restrictions.all.return_value = age_restrictions or []
        return drug

    @staticmethod
    def _make_qs(drugs):
        qs = MagicMock()
        qs.__iter__ = MagicMock(return_value=iter(drugs))
        qs.prefetch_related.return_value = drugs
        return qs

    def _run(self, drugs, human_data):
        qs = self._make_qs(drugs)
        with patch("ranker.views.Drug") as MockDrug:
            MockDrug.objects.filter.return_value.prefetch_related.return_value = qs
            return CalculationAPI()._exist_contraindications([1], human_data)

    def test_no_data(self):
        assert self._run([self._make_drug()], {"cont_list": [], "age": None}) == []

    def test_explicit(self):
        drug = self._make_drug(name="Аспирин", explicit=["язва"])
        assert self._run([drug], {"cont_list": [10], "age": None}) == \
            [("Аспирин", ["язва"])]

    def test_age_below_min(self):
        r = MagicMock(age_from=18, age_to=None)
        drug = self._make_drug(name="Аспирин", age_restrictions=[r])
        assert self._run([drug], {"cont_list": [], "age": 10}) == \
            [("Аспирин", ["возраст до 18 лет"])]

    def test_age_above_max(self):
        r = MagicMock(age_from=None, age_to=65)
        drug = self._make_drug(name="Аспирин", age_restrictions=[r])
        assert self._run([drug], {"cont_list": [], "age": 80}) == \
            [("Аспирин", ["возраст после 65 лет"])]

    def test_both(self):
        r = MagicMock(age_from=18, age_to=None)
        drug = self._make_drug(name="Аспирин", explicit=["язва"], age_restrictions=[r])
        assert self._run([drug], {"cont_list": [10], "age": 10}) == \
            [("Аспирин", ["язва", "возраст до 18 лет"])]

    def test_none(self):
        drug = self._make_drug(name="Аспирин")
        drug.age_restrictions.all.return_value = [MagicMock(age_from=18, age_to=65)]
        assert self._run([drug], {"cont_list": [], "age": 30}) == []


class TestCreateBannedResponse:

    def test_updates_template(self):
        template = {"bannedPairs": [], "compatibility_fortran": None}
        banned = [{"pair": ["A", "B"], "comment": "x"}]

        response = CalculationAPI()._create_banned_response(template, banned)

        assert response.status_code == 200
        body = response.data["data"]
        assert body["compatibility_fortran"] == CalculationAPI.COMPATIBILITY_BANNED
        assert body["bannedPairs"] == banned


class TestCreateContraindicationsResponse:

    def test_updates_template(self):
        contras = [("Аспирин", ["язва", "астма"]), ("Варфарин", ["кровотечение"])]

        response = CalculationAPI()._create_contraindications_response({}, contras)

        body = response.data["data"]
        assert body["compatibility_fortran"] == \
            CalculationAPI.COMPATIBILITY_BANNED_CONTRAINDICATIONS
        assert body["bannedPairsCont"] == [
            {"drug": "Аспирин", "contraindications": ["язва", "астма"]},
            {"drug": "Варфарин", "contraindications": ["кровотечение"]},
        ]

    def test_empty(self):
        response = CalculationAPI()._create_contraindications_response({}, [])
        assert response.data["data"]["bannedPairsCont"] == []


class TestCalculateCompatibility:

    def test_weights_validation_error(self, api):
        with patch.object(api, "_validate_weights_completeness") as mock_val:
            mock_val.return_value = CustomResponse(status=400, message="weights",
                                                   http_status=400)
            result = api._calculate_compatibility({}, [1, 2], True, None)
        assert isinstance(result, CustomResponse)

    @patch("ranker.views.FortranCalculator")
    def test_merges_context(self, MockCalc, api):
        MockCalc.return_value.calculate.return_value = {
            "compatibility_fortran": "compatible",
            "rank_iteractions": 0.3,
        }
        with patch.object(api, "_validate_weights_completeness", return_value=None):
            result = api._calculate_compatibility(
                {"drugs": ["A", "B"]}, [1, 2], True, None
            )
        assert result["drugs"] == ["A", "B"]
        assert result["compatibility_fortran"] == "compatible"
        assert result["rank_iteractions"] == 0.3

    @patch("ranker.views.FortranCalculator")
    def test_passes_normalize_and_gender(self, MockCalc, api):
        MockCalc.return_value.calculate.return_value = {"compatibility_fortran": "compatible"}
        with patch.object(api, "_validate_weights_completeness", return_value=None):
            api._calculate_compatibility({}, [1, 2], False, "man")
        assert MockCalc.call_args.kwargs["normalize"] is False
        assert MockCalc.return_value.calculate.call_args.kwargs["gender"] == "man"