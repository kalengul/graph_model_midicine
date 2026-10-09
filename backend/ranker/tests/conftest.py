"""Общие фикстуры для тестов ranker."""
import pytest
from rest_framework.test import APIRequestFactory

from side_effects.models import DrugSideEffect
from ranker.utils.fortran_calculator import FortranCalculator
from ranker.views import CalculationAPI


@pytest.fixture
def factory():
    return APIRequestFactory()


@pytest.fixture
def api():
    return CalculationAPI()


@pytest.fixture
def filled_db(three_drugs, three_side_effects):
    """Заполняет DrugSideEffect тестовыми рангами."""
    rank_matrix = [
        [0.06, 0.0, 0.3],
        [0.09, 0.2, 0.05],
        [0.1,  0.2, 0.04],
    ]
    DrugSideEffect.objects.all().delete()
    for i, drug in enumerate(three_drugs):
        for j, effect in enumerate(three_side_effects):
            DrugSideEffect.objects.create(
                drug=drug, side_effect=effect,
                rang_base=rank_matrix[i][j],
                rang_f1=0.0, rang_f2=0.0, rang_freq=0.0,
                rang_m1=0.0, rang_m2=0.0,
                probability=rank_matrix[i][j],
            )
    return three_drugs, three_side_effects


@pytest.fixture
def calculator_base(filled_db):
    return FortranCalculator(normalize=False, cuttoff_not_life_threats_side_e=False)


@pytest.fixture
def calculator_with_cutoff(filled_db):
    return FortranCalculator(normalize=False, cuttoff_not_life_threats_side_e=True)


@pytest.fixture
def calculator_with_canceling(filled_db):
    return FortranCalculator(normalize=True, cuttoff_not_life_threats_side_e=False)


@pytest.fixture
def calculator_full(filled_db):
    return FortranCalculator(normalize=True, cuttoff_not_life_threats_side_e=True)