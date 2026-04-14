import pytest
import numpy as np
from drugs.models import Drug, SideEffect, DrugSideEffect, SideEffectsGender, DrugGroup
from ranker.utils.fortran_calculator import FortranCalculatorNormalization

pytestmark = pytest.mark.django_db


# ------------------- Фикстуры для заполнения БД -------------------
@pytest.fixture
def filled_db(three_drugs, three_side_effects):
    """
    Заполняет таблицу DrugSideEffect тестовыми рангами.
    Возвращает кортеж (список препаратов, список побочных эффектов).
    """
    rank_matrix = [
        [0.06, 0,   0.3],
        [0.09, 0.2, 0.05],
        [0.1,  0.2, 0.04]
    ]
    # Очищаем старые связи (на случай, если они остались от других тестов)
    DrugSideEffect.objects.all().delete()
    for i, drug in enumerate(three_drugs):
        for j, effect in enumerate(three_side_effects):
            DrugSideEffect.objects.create(
                drug=drug,
                side_effect=effect,
                rang_base=rank_matrix[i][j],
                rang_f1=0.0, rang_f2=0.0, rang_freq=0.0, rang_m1=0.0, rang_m2=0.0,
                probability=rank_matrix[i][j]
            )
    return three_drugs, three_side_effects


# ------------------- Фикстуры калькуляторов (с данными) -------------------
@pytest.fixture
def calculator_base(filled_db):
    """Калькулятор без отсечки и без групп нивелирования, с реальными данными."""
    return FortranCalculatorNormalization(canceling_groups=None, cuttoff_not_life_threats_side_e=False)


@pytest.fixture
def calculator_with_cutoff(filled_db):
    """Калькулятор с отсечкой нежизнеугрожающих эффектов."""
    return FortranCalculatorNormalization(canceling_groups=None, cuttoff_not_life_threats_side_e=True)


@pytest.fixture
def calculator_with_canceling(filled_db):
    """Калькулятор с группой нивелирования (гипокалиемия и гиперкалиемия)."""
    return FortranCalculatorNormalization(canceling_groups=[[2, 3]], cuttoff_not_life_threats_side_e=False)


# ------------------- Тесты -------------------
class TestFortranCalculatorNormalization:

    def test_validate_canceling_groups_valid(self, calculator_base):
        groups = [[1, 2], [2, 3, 1]]
        valid = calculator_base._validate_canceling_groups(groups)
        assert valid == [[1, 2], [2, 3, 1]]

    def test_validate_canceling_groups_invalid(self, calculator_base):
        groups = [[1], [2, 100], "not list", [1, 2, 3]]
        valid = calculator_base._validate_canceling_groups(groups)
        assert valid == [[1, 2, 3]]

    def test_get_excluded_se_by_gender(self, calculator_base, three_side_effects):
        # Предварительно добавим гендерные связи (фикстура three_side_effects не создаёт их)
        se1 = SideEffect.objects.get(se_name="внутричерепное кровоизлияние")
        se2 = SideEffect.objects.get(se_name="гипокалиемия")
        se3 = SideEffect.objects.get(se_name="гиперкалиемия")
        SideEffectsGender.objects.get_or_create(side_effect=se1, gender='man')
        SideEffectsGender.objects.get_or_create(side_effect=se2, gender='woman')
        SideEffectsGender.objects.get_or_create(side_effect=se3, gender='man')

        excluded_man = calculator_base._get_excluded_se_by_gender('man')
        assert excluded_man == {se2.id}
        excluded_woman = calculator_base._get_excluded_se_by_gender('woman')
        assert excluded_woman == {se1.id, se3.id}

    def test_load_side_effects_dict(self, calculator_base, three_side_effects):
        excluded = {SideEffect.objects.get(se_name="гипокалиемия").id}
        id2side = calculator_base._load_side_effects_dict(excluded)
        # Ключи 0-индексация
        expected_ids = {se.id for se in three_side_effects if se.id not in excluded}
        expected = {se.id - 1: se.se_name for se in three_side_effects if se.id not in excluded}
        assert id2side == expected

    def test_build_rank_matrices(self, calculator_base, filled_db):
        three_drugs, _ = filled_db
        n_drug = [drug.id for drug in three_drugs[:2]]
        rangs_matrix, rang1, rangsum = calculator_base._build_rank_matrices(n_drug, 'rang_base')
        assert rangs_matrix.shape == (3, 3)
        assert rang1.shape == (2, 3)
        assert rangsum.shape == (3,)
        np.testing.assert_almost_equal(rangs_matrix[0], [0.06, 0, 0.3])
        np.testing.assert_almost_equal(rangs_matrix[1], [0.09, 0.2, 0.05])
        np.testing.assert_almost_equal(rangs_matrix[2], [0.1, 0.2, 0.04])
        np.testing.assert_almost_equal(rang1[0], [0.06, 0, 0.3])
        np.testing.assert_almost_equal(rang1[1], [0.09, 0.2, 0.05])
        np.testing.assert_almost_equal(rangsum, [0.15, 0.2, 0.35])

    def test_apply_canceling_normalization(self, calculator_with_canceling):
        rangsum = np.array([0.2, 0.5, 0.3])
        normalized = calculator_with_canceling._apply_canceling_normalization(rangsum)
        expected = np.array([0.2, 0.3125, 0.1125])
        np.testing.assert_almost_equal(normalized, expected)

    def test_cap_non_life_threatening(self, filled_db):
        # Устанавливаем для гипокалиемии и гиперкалиемии is_life_threatening=False
        se_hypokal = SideEffect.objects.get(se_name="гипокалиемия")
        se_hyperkal = SideEffect.objects.get(se_name="гиперкалиемия")
        se_hypokal.is_life_threatening = False
        se_hyperkal.is_life_threatening = False
        se_hypokal.save()
        se_hyperkal.save()

        # Создаём калькулятор ПОСЛЕ изменения флагов
        calculator = FortranCalculatorNormalization(canceling_groups=None, cuttoff_not_life_threats_side_e=True)
        rangsum = np.array([1.5, 0.8, 2.0])
        capped = calculator._cap_non_life_threatening(rangsum)
        expected = np.array([1.5, 0.8, 0.99])
        np.testing.assert_almost_equal(capped, expected)

    def test_classify_and_build_side_effects(self, calculator_base):
        rangsum = np.array([1.2, 0.6, 0.2])
        id2side = {0: "внутричерепное кровоизлияние", 1: "гипокалиемия", 2: "гиперкалиемия"}
        context = calculator_base._classify_and_build_side_effects(rangsum, id2side)
        assert context['compatibility_fortran'] == 'incompatible'
        assert len(context['side_effects'][2]['effects']) == 1
        assert len(context['side_effects'][0]['effects']) == 1
        assert context['side_effects'][2]['effects'][0]['se_name'] == "внутричерепное кровоизлияние"
        assert context['side_effects'][2]['effects'][0]['rank'] == 1.2

    def test_get_excluded_drugs_by_groups(self, calculator_base):
        # Создаём новых препаратов, чтобы избежать влияния фикстур
        from drugs.models import Drug, DrugGroup
        group = DrugGroup.objects.create(dg_name="Тестовая группа")
        drug1 = Drug.objects.create(drug_name="Тест1")
        drug2 = Drug.objects.create(drug_name="Тест2")
        drug3 = Drug.objects.create(drug_name="Тест3")
        drug1.drug_groups.add(group)
        drug2.drug_groups.add(group)
        # drug3 не добавляем в группу

        excluded = calculator_base._get_excluded_drugs_by_groups([drug1.id])
        # Ожидаем только drug2 (0-индекс = drug2.id - 1)
        assert excluded == {drug2.id - 1}

    def test_analyze_potential_drugs(self, calculator_base, filled_db):
        three_drugs, three_side_effects = filled_db
        n_drug = [three_drugs[0].id, three_drugs[1].id]
        rangs_matrix, rang1, rangsum = calculator_base._build_rank_matrices(n_drug, 'rang_base')
        id2side = {se.id - 1: se.se_name for se in three_side_effects}
        drugs_class_2, drugs_class_3 = calculator_base._analyze_potential_drugs(
            rangs_matrix, rangsum, n_drug, set(), id2side
        )
        # При данных рангах третий препарат не создаёт проблем
        assert len(drugs_class_2) == 0
        assert len(drugs_class_3) == 0

    def test_get_se_from_drugs(self, calculator_base, filled_db):
        three_drugs, _ = filled_db
        n_drug = [drug.id for drug in three_drugs[:2]]
        result = calculator_base._get_se_from_drugs(n_drug, set(), 'rang_base')
        assert len(result) == 2
        drug1_effects = result[0]['effects']
        assert len(drug1_effects) == 3
        ranks = [e['rank'] for e in drug1_effects]
        assert sorted(ranks, reverse=True) == [0.3, 0.06, 0.0]

    def test_calculate_compatible(self, calculator_base):
        result = calculator_base.calculate('rang_base', [1, 2])
        assert result['compatibility_fortran'] == 'compatible'
        assert result['rank_iteractions'] == 0.35
        assert len(result['side_effects'][2]['effects']) == 0

    def test_calculate_caution(self, calculator_base):
        pytest.skip("Нет подходящих данных для caution")

    def test_calculate_incompatible(self, calculator_base, filled_db):
        three_drugs, _ = filled_db
        drug_amiodarone = three_drugs[0]
        effect_hyperkal = SideEffect.objects.get(se_name="гиперкалиемия")
        dse = DrugSideEffect.objects.get(drug=drug_amiodarone, side_effect=effect_hyperkal)
        original = dse.rang_base
        dse.rang_base = 1.2
        dse.save()
        result = calculator_base.calculate('rang_base', [drug_amiodarone.id, three_drugs[2].id])
        assert result['compatibility_fortran'] == 'incompatible'
        dse.rang_base = original
        dse.save()

    def test_calculate_with_gender_exclusion(self, calculator_base, three_side_effects):
        # Добавим гендерные связи
        se1 = SideEffect.objects.get(se_name="внутричерепное кровоизлияние")
        se2 = SideEffect.objects.get(se_name="гипокалиемия")
        se3 = SideEffect.objects.get(se_name="гиперкалиемия")
        SideEffectsGender.objects.get_or_create(side_effect=se1, gender='man')
        SideEffectsGender.objects.get_or_create(side_effect=se2, gender='woman')
        SideEffectsGender.objects.get_or_create(side_effect=se3, gender='man')

        result_man = calculator_base.calculate('rang_base', [1, 2], gender='man')
        # Для мужчины исключена гипокалиемия (id=2), сумма рангов по оставшимся эффектам
        assert result_man['compatibility_fortran'] == 'compatible'
        # Проверяем, что в результатах нет гипокалиемии
        for se_list in result_man['side_effects']:
            for eff in se_list['effects']:
                assert eff['se_name'] != 'гипокалиемия'

    def test_calculate_with_canceling_normalization(self, calculator_with_canceling):
        result = calculator_with_canceling.calculate('rang_base', [1, 3])
        assert 'compatibility_fortran' in result

    def test_calculate_with_cutoff(self, filled_db):
        # Устанавливаем для гипокалиемии is_life_threatening=False
        se_hypokal = SideEffect.objects.get(id=2)
        se_hypokal.is_life_threatening = False
        se_hypokal.save()

        # Меняем ранг для гипокалиемии у амиодарона
        dse = DrugSideEffect.objects.get(drug_id=1, side_effect_id=2)
        original = dse.rang_base
        dse.rang_base = 1.5
        dse.save()

        # Создаём калькулятор ПОСЛЕ изменения флага и ранга
        calculator = FortranCalculatorNormalization(canceling_groups=None, cuttoff_not_life_threats_side_e=True)
        result = calculator.calculate('rang_base', [1])

        # Проверяем, что ранг гипокалиемии ограничен до 0.99
        found = False
        for se_list in result['side_effects']:
            for eff in se_list['effects']:
                if eff['se_name'] == 'гипокалиемия':
                    assert eff['rank'] == 0.99
                    found = True
        assert found

        # Восстанавливаем исходный ранг (опционально, тестовая БД всё равно пересоздаётся)
        dse.rang_base = original
        dse.save()