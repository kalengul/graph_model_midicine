"""Классификация и построение списка побочных эффектов."""
import numpy as np
import pytest


pytestmark = pytest.mark.django_db


class TestClassifyAndBuildSideEffects:

    def test_incompatible(self, calculator_base):
        rangsum = np.array([1.2, 0.6, 0.2])
        id2side = {0: "внутричерепное кровоизлияние",
                   1: "гипокалиемия",
                   2: "гиперкалиемия"}
        ctx = calculator_base._classify_and_build_side_effects(rangsum, id2side)
        assert ctx['compatibility_fortran'] == 'incompatible'
        assert len(ctx['side_effects'][2]['effects']) == 1
        assert len(ctx['side_effects'][0]['effects']) == 1
        assert ctx['side_effects'][2]['effects'][0]['se_name'] == "внутричерепное кровоизлияние"
        assert ctx['side_effects'][2]['effects'][0]['rank'] == 1.2

    def test_caution(self, calculator_base):
        rangsum = np.array([0.7, 0.4, 0.3])
        id2side = {0: "A", 1: "B", 2: "C"}
        ctx = calculator_base._classify_and_build_side_effects(rangsum, id2side)
        assert ctx['compatibility_fortran'] == 'caution'
        effects = ctx['side_effects'][1]['effects']
        assert len(effects) == 1 and effects[0]['se_name'] == "A"

    def test_compatible(self, calculator_base):
        rangsum = np.array([0.4, 0.3, 0.2])
        id2side = {0: "A", 1: "B", 2: "C"}
        ctx = calculator_base._classify_and_build_side_effects(rangsum, id2side)
        assert ctx['compatibility_fortran'] == 'compatible'
        assert ctx['side_effects'][1]['effects'] == []
        assert ctx['side_effects'][2]['effects'] == []