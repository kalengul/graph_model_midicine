"""Тесты для _analyze_max_drug_contribution: unit + natural flow."""

import numpy as np
import pytest
from unittest.mock import MagicMock

from ranker.utils.fortran_calculator import FortranCalculator


# =========================================================================
# Fakes — единый набор для всех уровней тестов
# =========================================================================

class FakeGroup:
    def __init__(self, gid, name):
        self.id = gid
        self.dg_name = name


class FakeValuesList:
    """Имитация ValuesListQuerySet: distinct() + итерация + len."""
    def __init__(self, items):
        self._items = list(items)

    def distinct(self):
        seen, result = set(), []
        for x in self._items:
            if x not in seen:
                seen.add(x)
                result.append(x)
        return FakeValuesList(result)

    def __iter__(self): return iter(self._items)
    def __len__(self): return len(self._items)


class FakeGroupsManager:
    def __init__(self, groups):
        self._groups = list(groups)

    def all(self): return list(self._groups)

    def values_list(self, field, flat=False):
        if flat:
            return FakeValuesList([getattr(g, field) for g in self._groups])
        return FakeValuesList([(getattr(g, field),) for g in self._groups])


class FakeDrug:
    def __init__(self, did, name, groups=None):
        self.id = did
        self.drug_name = name
        self.drug_groups = FakeGroupsManager(groups or [])


class FakeDrugQuerySet:
    def __init__(self, items):
        self._items = list(items)

    def prefetch_related(self, *a): return self
    def only(self, *a): return self

    def exclude(self, id__in):
        ids = set(id__in)
        return FakeDrugQuerySet([d for d in self._items if d.id not in ids])

    def distinct(self):
        seen, result = set(), []
        for d in self._items:
            if d.id not in seen:
                seen.add(d.id)
                result.append(d)
        return FakeDrugQuerySet(result)

    def values_list(self, field, flat=False):
        if flat:
            return FakeValuesList([getattr(d, field) for d in self._items])
        return FakeValuesList([(getattr(d, field),) for d in self._items])

    def __iter__(self): return iter(self._items)
    def __len__(self): return len(self._items)


class FakeDrugManager:
    def __init__(self, all_drugs):
        self._all = list(all_drugs)

    def filter(self, **kwargs):
        results = list(self._all)
        if 'id__in' in kwargs:
            ids = set(kwargs['id__in'])
            results = [d for d in results if d.id in ids]
        if 'drug_groups__id__in' in kwargs:
            gids = set(kwargs['drug_groups__id__in'])
            results = [
                d for d in results
                if any(g.id in gids for g in d.drug_groups.all())
            ]
        return FakeDrugQuerySet(results)

    def count(self): return len(self._all)

    def get(self, **kwargs):
        for d in self._all:
            if all(getattr(d, k, None) == v for k, v in kwargs.items()):
                return d
        raise LookupError(f"Drug matching {kwargs} not found")


class FakeSideEffect:
    def __init__(self, sid, name, is_life_threatening=False):
        self.id = sid
        self.se_name = name
        self.is_life_threatening = is_life_threatening


class FakeSideEffectQuerySet:
    def __init__(self, items):
        self._items = list(items)
    def only(self, *a): return self
    def __iter__(self): return iter(self._items)


class FakeSideEffectManager:
    def __init__(self, items):
        self._all = list(items)
    def all(self): return FakeSideEffectQuerySet(self._all)
    def count(self): return len(self._all)
    def get(self, **kwargs):
        for se in self._all:
            if all(getattr(se, k, None) == v for k, v in kwargs.items()):
                return se
        raise LookupError(f"SideEffect {kwargs} not found")


class FakeDSE:
    """Одна запись DrugSideEffect."""
    def __init__(self, drug_id, se, rang_base=0.0):
        self.drug_id = drug_id
        self.side_effect = se
        self.side_effect_id = se.id
        self.rang_base = rang_base


class FakeDSEQuerySet:
    def __init__(self, items):
        self._items = list(items)
    def select_related(self, *a): return self
    def only(self, *a): return self

    def order_by(self, *fields):
        return FakeDSEQuerySet(sorted(
            self._items,
            key=lambda x: tuple(getattr(x, f) for f in fields),
        ))

    def values_list(self, field, flat=False):
        if flat:
            return [getattr(x, field) for x in self._items]
        return [(getattr(x, field),) for x in self._items]

    def filter(self, **kwargs):
        items = list(self._items)
        if 'drug_id__in' in kwargs:
            ids = set(kwargs['drug_id__in'])
            items = [x for x in items if x.drug_id in ids]
        return FakeDSEQuerySet(items)

    def __iter__(self): return iter(self._items)


class FakeDSEManager:
    def __init__(self, items):
        self._all = list(items)
    def order_by(self, *fields):
        return FakeDSEQuerySet(self._all).order_by(*fields)
    def filter(self, **kwargs):
        return FakeDSEQuerySet(self._all).filter(**kwargs)


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def calc():
    """Unit-level: прямой вызов _analyze_max_drug_contribution, без DB."""
    c = FortranCalculator.__new__(FortranCalculator)
    c.normalize = False
    c.cuttoff_not_life_threats_side_e = False
    c.canceling_groups = []
    c._life_threatening_map = {}
    c.n_side_effect = 0
    c.n_drug = 0
    return c


@pytest.fixture
def install_drugs(monkeypatch):
    """Для unit-level: подменяет только Drug.objects."""
    def _install(drugs):
        mock = MagicMock()
        mock.objects = FakeDrugManager(drugs)
        monkeypatch.setattr(f"{FortranCalculator.__module__}.Drug", mock)
    return _install


@pytest.fixture
def calc_natural():
    """
    Natural flow: калькулятор для calculate() с normalize и опциональным cutoff.
    По умолчанию все эффекты life-threatening — cutoff не трогает.
    """
    c = FortranCalculator.__new__(FortranCalculator)
    c.normalize = True
    c.cuttoff_not_life_threats_side_e = False
    c.n_side_effect = 3
    c.n_drug = 4
    c.canceling_groups = [[2, 3]]   # пара из CANCELING_EFFECTS_GROUPS
    c._life_threatening_map = {1: True, 2: True, 3: True}
    return c


@pytest.fixture
def install_all_models(monkeypatch):
    """Для natural flow: подменяет Drug, SideEffect, DrugSideEffect."""
    def _install(drugs, side_effects, dses):
        for name, manager_obj in [
            ('Drug', FakeDrugManager(drugs)),
            ('SideEffect', FakeSideEffectManager(side_effects)),
            ('DrugSideEffect', FakeDSEManager(dses)),
        ]:
            mock = MagicMock()
            mock.objects = manager_obj
            monkeypatch.setattr(
                f"{FortranCalculator.__module__}.{name}", mock,
            )
    return _install


pytestmark = pytest.mark.django_db


# =========================================================================
# Часть 1. Unit-level — прямой вызов _analyze_max_drug_contribution
# =========================================================================

class TestContract:
    """Контракт: возвращаемое значение, пустые входы, неизвестные эффекты."""

    def test_no_effects(self, calculator_base):
        recs = calculator_base._analyze_max_drug_contribution(
            [], np.array([]), [], np.array([]), {},
        )
        assert recs == []

    def test_return_type_is_always_list(self, calculator_base):
        cases = [
            ([], np.array([]), [], np.array([]), {}),
            ([{'se_name': 'x'}], np.zeros((1, 1)), [], np.zeros(1), {'x': 0}),
            ([{'se_name': 'unknown'}], np.zeros((1, 1)), [1], np.zeros(1), {}),
        ]
        for args in cases:
            result = calculator_base._analyze_max_drug_contribution(*args)
            assert isinstance(result, list), (
                f"Ожидался list, получен {type(result).__name__}"
            )


class TestBasicReplacement:
    """Замена в рамках одной группы, один-два эффекта."""

    def test_single_effect_replacement_found_in_same_group(
        self, calc, install_drugs,
    ):
        calc.n_side_effect, calc.n_drug = 3, 3
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
            FakeDrug(3, 'Drug3', []),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}],
            np.array([[1.5, 0, 0], [0.2, 0, 0], [0.1, 0, 0]]),
            [1], np.array([1.5, 0, 0]),
            {'eff0': 0, 'eff1': 1, 'eff2': 2},
        )
        assert recs == [{
            'group_name': 'Group A',
            'drugs': [{'drug_name': 'Drug1', 'replace_drugs': ['Drug2']}],
        }]

    def test_multiple_effects_incompatible_replacement_fixes_all(
        self, calc, install_drugs,
    ):
        calc.n_side_effect, calc.n_drug = 3, 3
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
            FakeDrug(3, 'Drug3', [gA]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}, {'se_name': 'eff1'}],
            np.array([[1.5, 1.2, 0], [0.1, 0.2, 0], [0, 0.3, 0]]),
            [1], np.array([1.5, 1.2, 0]),
            {'eff0': 0, 'eff1': 1, 'eff2': 2},
        )
        assert len(recs) == 1
        assert set(recs[0]['drugs'][0]['replace_drugs']) == {'Drug2', 'Drug3'}


class TestMultipleRedZones:
    """Несколько красных зон от разных доминантов."""

    def test_two_red_zones_different_dominants_no_replacement(
        self, calc, install_drugs,
    ):
        calc.n_side_effect, calc.n_drug = 2, 4
        gA = FakeGroup(1, 'Group A')
        install_drugs([FakeDrug(i, f'Drug{i}', [gA]) for i in range(1, 5)])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}, {'se_name': 'eff1'}],
            np.array([[0.6, 0.5], [0.5, 0.6], [0.45, 0.45], [0.45, 0.45]]),
            [1, 2], np.array([1.1, 1.1]),
            {'eff0': 0, 'eff1': 1},
        )
        assert recs == []

    def test_two_red_zones_removed_when_replacement_covers_both(
        self, calc, install_drugs,
    ):
        calc.n_side_effect, calc.n_drug = 2, 4
        gA = FakeGroup(1, 'Group A')
        install_drugs([FakeDrug(i, f'Drug{i}', [gA]) for i in range(1, 5)])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}, {'se_name': 'eff1'}],
            np.array([[0.6, 0.5], [0.5, 0.6], [0.2, 0.2], [0.3, 0.3]]),
            [1, 2], np.array([1.1, 1.1]),
            {'eff0': 0, 'eff1': 1},
        )
        by_name = {d['drug_name']: set(d['replace_drugs'])
                   for d in recs[0]['drugs']}
        assert by_name == {'Drug1': {'Drug3', 'Drug4'},
                           'Drug2': {'Drug3', 'Drug4'}}

    def test_two_red_zones_asymmetric_replacements(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 2, 4
        gA = FakeGroup(1, 'Group A')
        install_drugs([FakeDrug(i, f'Drug{i}', [gA]) for i in range(1, 5)])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}, {'se_name': 'eff1'}],
            np.array([[0.6, 0.5], [0.5, 0.6], [0.2, 0.45], [0.45, 0.2]]),
            [1, 2], np.array([1.1, 1.1]),
            {'eff0': 0, 'eff1': 1},
        )
        by_name = {d['drug_name']: d['replace_drugs']
                   for d in recs[0]['drugs']}
        assert by_name == {'Drug1': ['Drug4'], 'Drug2': ['Drug3']}

    def test_replacement_fixes_only_one_of_three_no_recommendation(
        self, calc, install_drugs,
    ):
        """Прод-сценарий: фуросемид → торасемид не гасит qt/br."""
        calc.n_side_effect, calc.n_drug = 3, 4
        gA = FakeGroup(1, 'Антиаритмические')
        gD = FakeGroup(2, 'Диуретики')
        install_drugs([
            FakeDrug(1, 'амиодарон', [gA]),
            FakeDrug(2, 'ивабрадин', [gA]),
            FakeDrug(3, 'фуросемид', [gD]),
            FakeDrug(4, 'торасемид', [gD]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'qt'}, {'se_name': 'br'}, {'se_name': 'hyp'}],
            np.array([
                [0.65, 0.35, 0.10],
                [0.35, 0.60, 0.10],
                [0.30, 0.23, 0.81],
                [0.00, 0.17, 0.78],
            ]),
            [1, 2, 3], np.array([1.30, 1.18, 1.01]),
            {'qt': 0, 'br': 1, 'hyp': 2},
        )
        assert recs == []

    def test_replacement_fixes_all_three_zones(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 3, 4
        gA = FakeGroup(1, 'Антиаритмические')
        gD = FakeGroup(2, 'Диуретики')
        install_drugs([
            FakeDrug(1, 'амиодарон', [gA]),
            FakeDrug(2, 'ивабрадин', [gA]),
            FakeDrug(3, 'фуросемид', [gD]),
            FakeDrug(4, 'торасемид', [gD]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'qt'}, {'se_name': 'br'}, {'se_name': 'hyp'}],
            np.array([
                [0.55, 0.20, 0.10],
                [0.25, 0.60, 0.10],
                [0.35, 0.30, 0.81],
                [0.00, 0.00, 0.78],
            ]),
            [1, 2, 3], np.array([1.15, 1.10, 1.01]),
            {'qt': 0, 'br': 1, 'hyp': 2},
        )
        assert recs == [{
            'group_name': 'Диуретики',
            'drugs': [{'drug_name': 'фуросемид',
                       'replace_drugs': ['торасемид']}],
        }]

    def test_independent_incompatibilities_not_fixable(
        self, calc, install_drugs,
    ):
        calc.n_side_effect, calc.n_drug = 2, 2
        gA = FakeGroup(1, 'Group A')
        gB = FakeGroup(2, 'Group B')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gB]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}, {'se_name': 'eff1'}],
            np.array([[1.5, 0], [0, 1.2]]),
            [1, 2], np.array([1.5, 1.2]),
            {'eff0': 0, 'eff1': 1},
        )
        assert recs == []


class TestGroupIsolation:
    """Замена ищется строго в рамках одной фармакологической группы."""

    def test_replacement_only_within_same_group(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 2, 2
        gA = FakeGroup(1, 'Group A')
        gB = FakeGroup(2, 'Group B')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gB]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}],
            np.array([[1.5, 0], [0.1, 0]]),
            [1], np.array([1.5, 0]),
            {'eff0': 0, 'eff1': 1},
        )
        assert recs == []

    def test_candidate_in_other_group_is_ignored(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 2, 3
        gA = FakeGroup(1, 'Group A')
        gB = FakeGroup(2, 'Group B')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
            FakeDrug(3, 'Drug3', [gB]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}],
            np.array([[1.5, 0], [1.2, 0], [0.1, 0]]),
            [1], np.array([1.5, 0]),
            {'eff0': 0, 'eff1': 1},
        )
        assert recs == []


class TestGuardConditions:
    """Прочие защитные условия."""

    def test_no_suitable_replacement(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 2, 3
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
            FakeDrug(3, 'Drug3', [gA]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}, {'se_name': 'eff1'}],
            np.array([[1.5, 1.2], [1.0, 0.1], [0.1, 1.1]]),
            [1], np.array([1.5, 1.2]),
            {'eff0': 0, 'eff1': 1},
        )
        assert recs == []

    def test_alternative_already_selected_not_suggested(
        self, calc, install_drugs,
    ):
        calc.n_side_effect, calc.n_drug = 2, 2
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}],
            np.array([[1.5, 0], [0.1, 0]]),
            [1, 2], np.array([1.6, 0]),
            {'eff0': 0, 'eff1': 1},
        )
        assert recs == []

    def test_drug_not_in_max_drugs_not_recommended(
        self, calc, install_drugs,
    ):
        calc.n_side_effect, calc.n_drug = 2, 2
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}],
            np.array([[0.5, 0], [1.5, 0]]),
            [2], np.array([1.5, 0]),
            {'eff0': 0, 'eff1': 1},
        )
        assert recs[0]['drugs'] == [
            {'drug_name': 'Drug2', 'replace_drugs': ['Drug1']}
        ]

    def test_alternative_rejected_if_it_introduces_new_incompatibility(
        self, calc, install_drugs,
    ):
        calc.n_side_effect, calc.n_drug = 3, 2
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}],
            np.array([[1.5, 0, 0], [0.1, 1.2, 0]]),
            [1], np.array([1.5, 0, 0]),
            {'eff0': 0, 'eff1': 1, 'eff2': 2},
        )
        assert recs == []

    def test_effects_can_be_wrapped_in_dict(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 2, 2
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
        ])
        recs = calc._analyze_max_drug_contribution(
            {'effects': [{'se_name': 'eff0'}]},
            np.array([[1.5, 0], [0.1, 0]]),
            [1], np.array([1.5, 0]),
            {'eff0': 0, 'eff1': 1},
        )
        assert len(recs) == 1
        assert 'Drug2' in recs[0]['drugs'][0]['replace_drugs']

    def test_effect_key_can_be_name(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 2, 2
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'name': 'eff0'}],
            np.array([[1.5, 0], [0.1, 0]]),
            [1], np.array([1.5, 0]),
            {'eff0': 0, 'eff1': 1},
        )
        assert len(recs) == 1
        assert 'Drug2' in recs[0]['drugs'][0]['replace_drugs']


class TestNormalizeCutoffInAlternatives:
    """Unit-level: normalize/cutoff применяются к альтернативам (мок-проверка)."""

    def test_normalization_applied_to_alternatives(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 2, 2
        calc.normalize = True
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
        ])
        calls = []

        def fake_normalize(rs):
            calls.append(rs.copy())
            return np.zeros_like(rs)

        calc._apply_canceling_normalization = fake_normalize
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}],
            np.array([[1.5, 0], [0.5, 0]]),
            [1], np.array([1.5, 0]),
            {'eff0': 0, 'eff1': 1},
        )
        assert len(calls) >= 1
        assert 'Drug2' in recs[0]['drugs'][0]['replace_drugs']

    def test_cutoff_applied_to_alternatives(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 2, 2
        calc.cuttoff_not_life_threats_side_e = True
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
        ])
        calls = []

        def fake_cap(rs):
            calls.append(rs.copy())
            capped = rs.copy()
            capped[0] = min(capped[0], 0.99)
            return capped

        calc._cap_non_life_threatening = fake_cap
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}],
            np.array([[1.5, 0], [1.2, 0]]),
            [1], np.array([1.5, 0]),
            {'eff0': 0, 'eff1': 1},
        )
        assert len(calls) >= 1
        assert 'Drug2' in recs[0]['drugs'][0]['replace_drugs']


class TestExcludedEffects:
    """Исключённые (по полу) эффекты не блокируют рекомендацию."""

    def test_excluded_red_effect_does_not_block(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 3, 2
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}],
            np.array([[1.5, 0, 1.5], [0.1, 0, 1.5]]),
            [1], np.array([1.5, 0, 1.5]),
            {'eff0': 0, 'eff1': 1},   # eff2 отсутствует — исключён
        )
        assert recs == [{
            'group_name': 'Group A',
            'drugs': [{'drug_name': 'Drug1', 'replace_drugs': ['Drug2']}],
        }]

    def test_allowed_red_effect_still_blocks(self, calc, install_drugs):
        calc.n_side_effect, calc.n_drug = 3, 2
        gA = FakeGroup(1, 'Group A')
        install_drugs([
            FakeDrug(1, 'Drug1', [gA]),
            FakeDrug(2, 'Drug2', [gA]),
        ])
        recs = calc._analyze_max_drug_contribution(
            [{'se_name': 'eff0'}],
            np.array([[1.5, 0, 1.5], [0.1, 1.5, 1.5]]),
            [1], np.array([1.5, 0, 1.5]),
            {'eff0': 0, 'eff1': 1, 'eff2': 2},   # eff1 РАЗРЕШЁН
        )
        assert recs == []


# =========================================================================
# Часть 2. Natural flow — через calculate() с замоканными моделями
# =========================================================================
#
# Идея: не подсовывать rangsum/matrix руками, а дать «сырые» DrugSideEffect
# и позволить calculate() построить всё самому. Это ловит рассогласования
# между нормализованным rangsum и сырой матрицей, которые unit-тесты
# (с заранее собранными входами) не видят.
#
# Для отслеживания normalize/cutoff используем spy на приватные методы:
# - Первый вызов — на сырой rangsum из _build_rank_matrices
# - Последующие вызовы — на new_total альтернатив в _find_candidates_for_drug


def _effect_names(result, class_idx):
    """Имена эффектов в классе: 0=compatible, 1=caution, 2=incompatible."""
    return [e['se_name'] for e in result['side_effects'][class_idx]['effects']]


def _setup_4drug_2groups(install_all_models):
    """
    Стандартный сеттинг: 4 препарата, 2 группы, 3 эффекта.
    Возвращает (drugs, name_to_id, side_effects).
    """
    gA = FakeGroup(1, 'Антиаритмические')
    gD = FakeGroup(2, 'Диуретики')
    drugs = [
        FakeDrug(1, 'амиодарон', [gA]),
        FakeDrug(2, 'ивабрадин', [gA]),
        FakeDrug(3, 'фуросемид', [gD]),
        FakeDrug(4, 'торасемид', [gD]),
    ]
    se_hyp = FakeSideEffect(1, 'гипотензия')
    se_qt = FakeSideEffect(2, 'удлинение интервала qt')
    se_br = FakeSideEffect(3, 'брадикардия')
    return drugs, {d.drug_name: d.id for d in drugs}, [se_hyp, se_qt, se_br]


class TestNaturalFlowSemantics:
    """Семантические проверки через реальный calculate()."""

    def test_recommendation_must_resolve_incompatibility(
        self, calc_natural, install_all_models,
    ):
        """
        Если рекомендация выдана — её применение через тот же calculate()
        НЕ должно давать INCOMPATIBLE.

        На коде с багом «проверка < 1.0 идёт по рассогласованным значениям»
        — падает.
        """
        drugs, name_to_id, ses = _setup_4drug_2groups(install_all_models)

        # Убираем normalize и cutoff, чтобы видеть сырые значения
        calc_natural.normalize = False
        calc_natural.canceling_groups = []
        calc_natural.cuttoff_not_life_threats_side_e = False

        dses = [
            FakeDSE(1, ses[0], 0.10), FakeDSE(1, ses[1], 0.65), FakeDSE(1, ses[2], 0.35),
            FakeDSE(2, ses[0], 0.10), FakeDSE(2, ses[1], 0.35), FakeDSE(2, ses[2], 0.60),
            FakeDSE(3, ses[0], 0.81), FakeDSE(3, ses[1], 0.30), FakeDSE(3, ses[2], 0.23),
            FakeDSE(4, ses[0], 0.78), FakeDSE(4, ses[1], 0.00), FakeDSE(4, ses[2], 0.17),
        ]
        install_all_models(drugs, ses, dses)

        initial_ids = {1, 2, 3}
        result = calc_natural.calculate('rang_base', sorted(initial_ids))
        assert result['compatibility_fortran'] == 'incompatible'

        recs = result['rep_recommendations']
        if not recs:
            return  # нет рекомендаций — проверять нечего

        for group in recs:
            for drug_rec in group['drugs']:
                old_id = name_to_id[drug_rec['drug_name']]
                for new_name in drug_rec['replace_drugs']:
                    new_id = name_to_id[new_name]
                    new_ids = sorted((initial_ids - {old_id}) | {new_id})
                    new_result = calc_natural.calculate('rang_base', new_ids)

                    assert new_result['compatibility_fortran'] != 'incompatible', (
                        f"Баг: рекомендация заменить "
                        f"'{drug_rec['drug_name']}' на '{new_name}' "
                        f"не устраняет несовместимость.\n"
                        f"  Было: rank={result['rank_iteractions']}\n"
                        f"  Стало: rank={new_result['rank_iteractions']}\n"
                        f"  Остаются в incompatible: "
                        f"{_effect_names(new_result, 2)}"
                    )


class TestNaturalFlowNormalize:
    """Отслеживание normalize через реальный calculate()."""

    def test_normalize_changes_classification(
        self, calc_natural, install_all_models,
    ):
        """
        Демонстрирует, что normalize реально применяется и меняет класс:
        qt с сырым 1.30 попадает в incompatible; после нормализации
        с парой br — в caution.

        Сырые суммы (drug1 + drug3): hyp=0.20, qt=1.30, br=0.60.
        После normalize по паре [2, 3] (qt + br):
            qt_norm = 1.30² / (1.30 + 0.60) = 0.889  → caution
            br_norm = 0.60² / 1.90           = 0.189  → compatible
        """
        drugs, _, ses = _setup_4drug_2groups(install_all_models)
        dses = [
            FakeDSE(1, ses[0], 0.10), FakeDSE(1, ses[1], 0.65), FakeDSE(1, ses[2], 0.30),
            FakeDSE(2, ses[0], 0.00), FakeDSE(2, ses[1], 0.00), FakeDSE(2, ses[2], 0.00),
            FakeDSE(3, ses[0], 0.10), FakeDSE(3, ses[1], 0.65), FakeDSE(3, ses[2], 0.30),
            FakeDSE(4, ses[0], 0.00), FakeDSE(4, ses[1], 0.00), FakeDSE(4, ses[2], 0.00),
        ]
        install_all_models(drugs, ses, dses)

        # --- Без normalize: qt_raw = 1.30 → incompatible ---
        calc_natural.normalize = False
        calc_natural.canceling_groups = []
        raw_result = calc_natural.calculate('rang_base', [1, 3])

        assert raw_result['compatibility_fortran'] == 'incompatible', (
            f"Ожидалось INCOMPATIBLE, получено "
            f"{raw_result['compatibility_fortran']} "
            f"(rank={raw_result['rank_iteractions']})"
        )
        assert raw_result['rank_iteractions'] == 1.30, (
            f"Сырой max должен быть 1.30, получено "
            f"{raw_result['rank_iteractions']}"
        )
        assert 'удлинение интервала qt' in _effect_names(raw_result, 2), (
            f"qt должен быть в incompatible, "
            f"а там: {_effect_names(raw_result, 2)}"
        )

        # --- С normalize: qt = 1.30²/1.90 ≈ 0.889 → caution ---
        calc_natural.normalize = True
        calc_natural.canceling_groups = [[2, 3]]   # 1-based ID qt/br → индексы 1, 2
        norm_result = calc_natural.calculate('rang_base', [1, 3])

        assert norm_result['compatibility_fortran'] == 'caution', (
            f"Ожидалось CAUTION, получено "
            f"{norm_result['compatibility_fortran']} "
            f"(rank={norm_result['rank_iteractions']})"
        )
        assert norm_result['rank_iteractions'] == 0.89, (
            f"После normalize max должен быть ≈0.89, получено "
            f"{norm_result['rank_iteractions']}"
        )
        assert 'удлинение интервала qt' not in _effect_names(norm_result, 2), (
            "После normalize qt должен выйти из incompatible"
        )
        assert 'удлинение интервала qt' in _effect_names(norm_result, 1), (
            f"После normalize qt должен попасть в caution; "
            f"caution = {_effect_names(norm_result, 1)}"
        )

    def test_normalize_tracks_call_on_main_rangsum_and_alternatives(
        self, calc_natural, install_all_models,
    ):
        """
        Spy: _apply_canceling_normalization вызывается:
        1) на сыром rangsum в calculate()
        2) повторно для каждой альтернативы в _find_candidates_for_drug
        """
        drugs, _, ses = _setup_4drug_2groups(install_all_models)
        # eff0 = ID 1 (не в группе), eff1 = ID 2, eff2 = ID 3 (в группе [2,3])
        dses = [
            FakeDSE(1, ses[0], 1.30), FakeDSE(1, ses[1], 0.10), FakeDSE(1, ses[2], 0.10),
            FakeDSE(2, ses[0], 0.30), FakeDSE(2, ses[1], 0.10), FakeDSE(2, ses[2], 0.10),
            FakeDSE(3, ses[0], 0.20), FakeDSE(3, ses[1], 1.10), FakeDSE(3, ses[2], 0.10),
            FakeDSE(4, ses[0], 0.10), FakeDSE(4, ses[1], 0.20), FakeDSE(4, ses[2], 0.20),
        ]
        install_all_models(drugs, ses, dses)

        calls = []
        orig = calc_natural._apply_canceling_normalization

        def spy(rs):
            calls.append(np.array(rs, copy=True))
            return orig(rs)

        calc_natural._apply_canceling_normalization = spy

        calc_natural.calculate('rang_base', [1, 3])

        # Первый вызов — сырая сумма выбранных препаратов:
        # Drug1 + Drug3 = [1.30, 0.10, 0.10] + [0.20, 1.10, 0.10] = [1.50, 1.20, 0.20]
        assert len(calls) >= 1, "normalize не вызывался"
        np.testing.assert_allclose(
            calls[0], [1.50, 1.20, 0.20], atol=1e-6,
            err_msg="Первый вызов normalize должен быть на сырой сумме",
        )
        # Минимум ещё один вызов — для альтернативы в _find_candidates_for_drug
        assert len(calls) >= 2, (
            f"normalize должен вызываться и для альтернатив, "
            f"а всего вызовов: {len(calls)}"
        )


class TestNaturalFlowCutoff:
    """Отслеживание cutoff через реальный calculate()."""

    def test_cutoff_caps_non_life_threatening(
        self, calc_natural, install_all_models,
    ):
        """
        С cutoff=True нежизнеугрожающий эффект с суммой 1.30
        обрезается до RANG_LIMIT=0.5 → incompatible становится caution.
        """
        drugs, _, ses = _setup_4drug_2groups(install_all_models)
        dses = [
            FakeDSE(1, ses[0], 0.65), FakeDSE(1, ses[1], 0.0), FakeDSE(1, ses[2], 0.0),
            FakeDSE(2, ses[0], 0.00), FakeDSE(2, ses[1], 0.0), FakeDSE(2, ses[2], 0.0),
            FakeDSE(3, ses[0], 0.65), FakeDSE(3, ses[1], 0.0), FakeDSE(3, ses[2], 0.0),
            FakeDSE(4, ses[0], 0.00), FakeDSE(4, ses[1], 0.0), FakeDSE(4, ses[2], 0.0),
        ]
        install_all_models(drugs, ses, dses)
        calc_natural.normalize = False
        calc_natural.canceling_groups = []

        # Без cutoff: eff0 = 1.30 → incompatible
        calc_natural.cuttoff_not_life_threats_side_e = False
        raw_result = calc_natural.calculate('rang_base', [1, 3])
        assert 'гипотензия' in _effect_names(raw_result, 2)

        # С cutoff: eff0 → 0.5 → caution (все эффекты non-life-threatening)
        calc_natural.cuttoff_not_life_threats_side_e = True
        calc_natural._life_threatening_map = {1: False, 2: False, 3: False}
        capped_result = calc_natural.calculate('rang_base', [1, 3])
        assert 'гипотензия' not in _effect_names(capped_result, 2)
        assert 'гипотензия' in _effect_names(capped_result, 1)

    def test_cutoff_tracks_call_on_main_rangsum_and_alternatives(
        self, calc_natural, install_all_models,
    ):
        """
        Spy: _cap_non_life_threatening вызывается:
        1) на rangsum_for_context в calculate()
        2) повторно для альтернатив в _find_candidates_for_drug
        """
        drugs, _, ses = _setup_4drug_2groups(install_all_models)
        dses = [
            FakeDSE(1, ses[0], 1.30), FakeDSE(1, ses[1], 0.0), FakeDSE(1, ses[2], 0.0),
            FakeDSE(2, ses[0], 0.30), FakeDSE(2, ses[1], 0.0), FakeDSE(2, ses[2], 0.0),
            FakeDSE(3, ses[0], 0.20), FakeDSE(3, ses[1], 1.10), FakeDSE(3, ses[2], 0.0),
            FakeDSE(4, ses[0], 0.10), FakeDSE(4, ses[1], 0.20), FakeDSE(4, ses[2], 0.0),
        ]
        install_all_models(drugs, ses, dses)
        calc_natural.normalize = False
        calc_natural.canceling_groups = []
        calc_natural.cuttoff_not_life_threats_side_e = True
        # eff1 (ID=2) — life-threatening, чтобы eff0 всё ещё был incompatible
        calc_natural._life_threatening_map = {1: False, 2: True, 3: False}

        calls = []
        orig = calc_natural._cap_non_life_threatening

        def spy(rs):
            calls.append(np.array(rs, copy=True))
            return orig(rs)

        calc_natural._cap_non_life_threatening = spy

        calc_natural.calculate('rang_base', [1, 3])

        # Первый вызов — rangsum_for_context = raw sum
        # (Drug1 + Drug3 = [1.50, 1.10, 0.0])
        assert len(calls) >= 1, "cutoff не вызывался"
        np.testing.assert_allclose(
            calls[0], [1.50, 1.10, 0.0], atol=1e-6,
            err_msg="Первый вызов cutoff должен быть на rangsum_for_context",
        )
        assert len(calls) >= 2, (
            f"cutoff должен вызываться и для альтернатив, "
            f"а всего вызовов: {len(calls)}"
        )


class TestNaturalFlowCombined:
    """normalize + cutoff одновременно."""

    def test_both_transforms_applied_in_correct_order(
        self, calc_natural, install_all_models,
    ):
        """
        Порядок в calculate(): normalize применяется до cutoff.
        Spy фиксирует оба вызова на rangsum_for_context и проверяет,
        что cutoff видит уже нормализованное значение.
        """
        drugs, _, ses = _setup_4drug_2groups(install_all_models)
        dses = [
            FakeDSE(1, ses[0], 0.65), FakeDSE(1, ses[1], 0.10), FakeDSE(1, ses[2], 0.10),
            FakeDSE(2, ses[0], 0.00), FakeDSE(2, ses[1], 0.00), FakeDSE(2, ses[2], 0.00),
            FakeDSE(3, ses[0], 0.65), FakeDSE(3, ses[1], 1.10), FakeDSE(3, ses[2], 0.10),
            FakeDSE(4, ses[0], 0.00), FakeDSE(4, ses[1], 0.00), FakeDSE(4, ses[2], 0.00),
        ]
        install_all_models(drugs, ses, dses)
        calc_natural.cuttoff_not_life_threats_side_e = True
        calc_natural._life_threatening_map = {1: False, 2: True, 3: False}

        normalize_inputs = []
        cutoff_inputs = []

        orig_norm = calc_natural._apply_canceling_normalization
        orig_cap = calc_natural._cap_non_life_threatening

        calc_natural._apply_canceling_normalization = (
            lambda rs: (normalize_inputs.append(np.array(rs, copy=True)),
                        orig_norm(rs))[1]
        )
        calc_natural._cap_non_life_threatening = (
            lambda rs: (cutoff_inputs.append(np.array(rs, copy=True)),
                        orig_cap(rs))[1]
        )

        calc_natural.calculate('rang_base', [1, 3])

        # normalize получил сырую сумму: [1.30, 1.20, 0.20]
        np.testing.assert_allclose(
            normalize_inputs[0], [1.30, 1.20, 0.20], atol=1e-6,
        )
        # cutoff получил уже нормализованное значение:
        # qt: 1.20²/1.40 ≈ 1.029, br: 0.20²/1.40 ≈ 0.029
        np.testing.assert_allclose(
            cutoff_inputs[0], [1.30, 1.029, 0.029], atol=1e-2,
            err_msg="cutoff должен видеть уже нормализованный rangsum",
        )
        # cutoff обрезал eff0 (non-life-threatening) до 0.5,
        # но eff1 (life-threatening) остался 1.029 → incompatible
        # Значит, cutoff_inputs[0] ещё не обрезан (это вход)
        assert cutoff_inputs[0][0] > 0.5, (
            "cutoff должен получать значение до обрезки"
        )