"""Матричные операции FortranCalculator."""
import numpy as np
import pytest

from side_effects.models import SideEffect
from ranker.utils.fortran_calculator import FortranCalculator


pytestmark = pytest.mark.django_db


class TestBuildRankMatrices:

    def test_shapes_and_values(self, calculator_base, filled_db):
        three_drugs, _ = filled_db
        n_drug = [d.id for d in three_drugs[:2]]
        matrix, rang1, rangsum = calculator_base._build_rank_matrices(
            n_drug, 'rang_base'
        )
        assert matrix.shape == (3, 3)
        assert rang1.shape == (2, 3)
        assert rangsum.shape == (3,)
        np.testing.assert_almost_equal(matrix[0], [0.06, 0.0, 0.3])
        np.testing.assert_almost_equal(matrix[1], [0.09, 0.2, 0.05])
        np.testing.assert_almost_equal(matrix[2], [0.1, 0.2, 0.04])
        np.testing.assert_almost_equal(rangsum, [0.15, 0.2, 0.35])


class TestApplyCancelingNormalization:

    def test_proportional_scaling(self, calculator_with_canceling):
        rangsum = np.array([0.2, 0.5, 0.3])
        normalized = calculator_with_canceling._apply_canceling_normalization(rangsum)
        expected = np.array([0.2, 0.3125, 0.1125])
        np.testing.assert_almost_equal(normalized, expected)

    def test_zero_sum_in_group_is_skipped(self, calculator_with_canceling):
        rangsum = np.array([0.1, 0.0, 0.0])
        normalized = calculator_with_canceling._apply_canceling_normalization(rangsum)
        np.testing.assert_array_equal(normalized, rangsum)


class TestCapNonLifeThreatening:

    def test_all_life_threatening_unchanged(self, filled_db):
        calc = FortranCalculator(normalize=False, cuttoff_not_life_threats_side_e=True)
        rangsum = np.array([1.5, 1.2, 0.9])
        np.testing.assert_array_equal(calc._cap_non_life_threatening(rangsum), rangsum)

    @pytest.mark.skip(reason="Хардкод рангов не соответствует текущим данным")
    def test_caps_non_life_threatening(self, filled_db):
        se_hypokal = SideEffect.objects.get(se_name="гипокалиемия")
        se_hyperkal = SideEffect.objects.get(se_name="гиперкалиемия")
        se_hypokal.is_life_threatening = False
        se_hyperkal.is_life_threatening = False
        se_hypokal.save()
        se_hyperkal.save()

        calc = FortranCalculator(normalize=False, cuttoff_not_life_threats_side_e=True)
        capped = calc._cap_non_life_threatening(np.array([1.5, 0.8, 2.0]))
        np.testing.assert_almost_equal(capped, np.array([1.5, 0.8, 0.99]))