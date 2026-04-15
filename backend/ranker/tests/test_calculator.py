import pytest
import numpy as np
from drugs.models import Drug, SideEffect, DrugSideEffect, SideEffectsGender, DrugGroup
from ranker.utils.fortran_calculator import FortranCalculator

pytestmark = pytest.mark.django_db


# ------------------- Фикстуры для заполнения БД -------------------
@pytest.fixture
def filled_db(three_drugs, three_side_effects):
    """
    Заполняет таблицу DrugSideEffect тестовыми рангами.

    Матрица рангов:
        [
            [0.06, 0.0, 0.3 ],
            [0.09, 0.2, 0.05],
            [0.1,  0.2, 0.04]
        ]

    Возвращает:
        tuple: (список препаратов, список побочных эффектов)
    """
    rank_matrix = [
        [0.06, 0.0, 0.3],
        [0.09, 0.2, 0.05],
        [0.1, 0.2, 0.04]
    ]

    # Очищаем старые связи
    DrugSideEffect.objects.all().delete()

    for i, drug in enumerate(three_drugs):
        for j, effect in enumerate(three_side_effects):
            DrugSideEffect.objects.create(
                drug=drug,
                side_effect=effect,
                rang_base=rank_matrix[i][j],
                rang_f1=0.0,
                rang_f2=0.0,
                rang_freq=0.0,
                rang_m1=0.0,
                rang_m2=0.0,
                probability=rank_matrix[i][j]
            )

    return three_drugs, three_side_effects


# ------------------- Фикстуры калькуляторов -------------------
@pytest.fixture
def calculator_base(filled_db):
    """Калькулятор без нормализации и без отсечки нежизнеугрожающих эффектов."""
    return FortranCalculator(
        normalize=False,
        cuttoff_not_life_threats_side_e=False
    )


@pytest.fixture
def calculator_with_cutoff(filled_db):
    """Калькулятор с отсечкой нежизнеугрожающих эффектов, без нормализации."""
    return FortranCalculator(
        normalize=False,
        cuttoff_not_life_threats_side_e=True
    )


@pytest.fixture
def calculator_with_canceling(filled_db):
    """Калькулятор с нормализацией (встроенные группы, включая гипо/гиперкалиемию)."""
    return FortranCalculator(
        normalize=True,
        cuttoff_not_life_threats_side_e=False
    )


@pytest.fixture
def calculator_full(filled_db):
    """Калькулятор с нормализацией и отсечкой."""
    return FortranCalculator(
        normalize=True,
        cuttoff_not_life_threats_side_e=True
    )


# ------------------- Тесты -------------------
class TestFortranCalculator:
    """
    Набор тестов для класса FortranCalculator.

    Проверяет:
        - валидацию групп нивелирования,
        - исключение побочных эффектов по полу,
        - построение матриц рангов,
        - нормализацию противоположных эффектов,
        - ограничение нежизнеугрожающих эффектов,
        - классификацию совместимости,
        - анализ потенциальных препаратов,
        - формирование рекомендаций.
    """

    def test_validate_canceling_groups_valid(self, calculator_base):
        """
        Проверка валидации корректных групп нивелирования.

        Ожидается, что все поданные группы, содержащие ≥2 валидных индекса,
        будут возвращены без изменений.
        """
        groups = [[1, 2], [2, 3, 1]]
        valid = calculator_base._validate_canceling_groups(groups)
        assert valid == [[1, 2], [2, 3, 1]]

    def test_validate_canceling_groups_invalid(self, calculator_base):
        """
        Проверка фильтрации некорректных групп нивелирования.

        Группы с одним элементом, нецелочисленными индексами или
        выходящими за пределы должны быть отброшены.
        """
        groups = [[1], [2, 100], "not list", [1, 2, 3]]
        valid = calculator_base._validate_canceling_groups(groups)
        assert valid == [[1, 2, 3]]

    def test_validate_canceling_groups_none(self, calculator_base):
        """Проверка, что при None возвращается None."""
        assert calculator_base._validate_canceling_groups(None) is None

    def test_validate_canceling_groups_not_list(self, calculator_base):
        """Проверка, что не-список приводит к None и логированию ошибки."""
        assert calculator_base._validate_canceling_groups("not_list") is None

    def test_get_excluded_se_by_gender(self, calculator_base, three_side_effects):
        """
        Проверка исключения побочных эффектов по полу.

        Для заданного пола исключаются эффекты, связанные с противоположным полом.
        """
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

    def test_get_excluded_se_by_gender_none(self, calculator_base):
        """При gender=None возвращается пустое множество."""
        assert calculator_base._get_excluded_se_by_gender(None) == set()

    def test_load_side_effects_dict(self, calculator_base, three_side_effects):
        """
        Проверка загрузки словаря побочных эффектов с учётом исключённых ID.

        Ключи словаря — 0-индексированные идентификаторы эффектов.
        """
        excluded = {SideEffect.objects.get(se_name="гипокалиемия").id}
        id2side = calculator_base._load_side_effects_dict(excluded)

        expected = {
            se.id - 1: se.se_name
            for se in three_side_effects
            if se.id not in excluded
        }
        assert id2side == expected

    def test_build_rank_matrices(self, calculator_base, filled_db):
        """
        Проверка построения матриц рангов.

        Возвращаются:
            - rangs_matrix: полная матрица (n_drug x n_side_effect),
            - rang1: матрица только для выбранных препаратов,
            - rangsum: сумма рангов по выбранным препаратам.
        """
        three_drugs, _ = filled_db
        n_drug = [drug.id for drug in three_drugs[:2]]
        rangs_matrix, rang1, rangsum = calculator_base._build_rank_matrices(
            n_drug, 'rang_base'
        )

        assert rangs_matrix.shape == (3, 3)
        assert rang1.shape == (2, 3)
        assert rangsum.shape == (3,)

        np.testing.assert_almost_equal(rangs_matrix[0], [0.06, 0.0, 0.3])
        np.testing.assert_almost_equal(rangs_matrix[1], [0.09, 0.2, 0.05])
        np.testing.assert_almost_equal(rangs_matrix[2], [0.1, 0.2, 0.04])

        np.testing.assert_almost_equal(rang1[0], [0.06, 0.0, 0.3])
        np.testing.assert_almost_equal(rang1[1], [0.09, 0.2, 0.05])

        np.testing.assert_almost_equal(rangsum, [0.15, 0.2, 0.35])

    def test_apply_canceling_normalization(self, calculator_with_canceling):
        """
        Проверка нормализации противоположных эффектов.

        Ранги в группе масштабируются пропорционально их вкладу.
        """
        rangsum = np.array([0.2, 0.5, 0.3])
        normalized = calculator_with_canceling._apply_canceling_normalization(rangsum)
        # Для группы [2,3] (индексы 1 и 2): сумма = 0.5+0.3=0.8
        # веса: 0.5/0.8=0.625, 0.3/0.8=0.375
        # новые значения: 0.5*0.625=0.3125, 0.3*0.375=0.1125
        expected = np.array([0.2, 0.3125, 0.1125])
        np.testing.assert_almost_equal(normalized, expected)

    def test_apply_canceling_normalization_zero_sum(self, calculator_with_canceling):
        """
        Проверка, что при нулевой сумме рангов в группе нормализация пропускается.
        """
        rangsum = np.array([0.1, 0.0, 0.0])
        normalized = calculator_with_canceling._apply_canceling_normalization(rangsum)
        np.testing.assert_array_equal(normalized, rangsum)

    def test_cap_non_life_threatening(self, filled_db):
        """
        Проверка ограничения ранга нежизнеугрожающих эффектов до 0.99.

        Эффекты с is_life_threatening=False обрезаются до 0.99.
        """
        se_hypokal = SideEffect.objects.get(se_name="гипокалиемия")
        se_hyperkal = SideEffect.objects.get(se_name="гиперкалиемия")
        se_hypokal.is_life_threatening = False
        se_hyperkal.is_life_threatening = False
        se_hypokal.save()
        se_hyperkal.save()

        calculator = FortranCalculator(
            normalize=False,
            cuttoff_not_life_threats_side_e=True
        )
        rangsum = np.array([1.5, 0.8, 2.0])
        capped = calculator._cap_non_life_threatening(rangsum)
        expected = np.array([1.5, 0.8, 0.99])
        np.testing.assert_almost_equal(capped, expected)

    def test_cap_non_life_threatening_all_life_threatening(self, filled_db):
        """Если все эффекты жизнеугрожающие, массив не изменяется."""
        # По умолчанию все эффекты жизнеугрожающие
        calculator = FortranCalculator(
            normalize=False,
            cuttoff_not_life_threats_side_e=True
        )
        rangsum = np.array([1.5, 1.2, 0.9])
        capped = calculator._cap_non_life_threatening(rangsum)
        np.testing.assert_array_equal(capped, rangsum)

    def test_classify_and_build_side_effects(self, calculator_base):
        """
        Проверка классификации общей комбинации и формирования списка эффектов.

        На основе максимального ранга определяется класс совместимости,
        эффекты распределяются по трём группам.
        """
        rangsum = np.array([1.2, 0.6, 0.2])
        id2side = {
            0: "внутричерепное кровоизлияние",
            1: "гипокалиемия",
            2: "гиперкалиемия"
        }
        context = calculator_base._classify_and_build_side_effects(rangsum, id2side)

        assert context['compatibility_fortran'] == 'incompatible'
        assert len(context['side_effects'][2]['effects']) == 1
        assert len(context['side_effects'][0]['effects']) == 1
        assert context['side_effects'][2]['effects'][0]['se_name'] == "внутричерепное кровоизлияние"
        assert context['side_effects'][2]['effects'][0]['rank'] == 1.2

    def test_classify_and_build_side_effects_caution(self, calculator_base):
        """Проверка классификации для случая 'caution'."""
        rangsum = np.array([0.7, 0.4, 0.3])
        id2side = {0: "A", 1: "B", 2: "C"}
        context = calculator_base._classify_and_build_side_effects(rangsum, id2side)
        assert context['compatibility_fortran'] == 'caution'
        # Эффекты с рангом >=0.5 должны быть в группе caution
        caution_effects = context['side_effects'][1]['effects']
        assert len(caution_effects) == 1
        assert caution_effects[0]['se_name'] == "A"

    def test_classify_and_build_side_effects_compatible(self, calculator_base):
        """Проверка классификации для случая 'compatible'."""
        rangsum = np.array([0.4, 0.3, 0.2])
        id2side = {0: "A", 1: "B", 2: "C"}
        context = calculator_base._classify_and_build_side_effects(rangsum, id2side)
        assert context['compatibility_fortran'] == 'compatible'
        assert len(context['side_effects'][1]['effects']) == 0
        assert len(context['side_effects'][2]['effects']) == 0

    def test_get_excluded_drugs_by_groups(self, calculator_base):
        """
        Проверка исключения препаратов, входящих в те же группы, что и выбранные.

        Препараты из тех же групп, не попавшие в исходный список, исключаются.
        """
        group = DrugGroup.objects.create(dg_name="Тестовая группа")
        drug1 = Drug.objects.create(drug_name="Тест1")
        drug2 = Drug.objects.create(drug_name="Тест2")
        drug3 = Drug.objects.create(drug_name="Тест3")

        drug1.drug_groups.add(group)
        drug2.drug_groups.add(group)
        # drug3 не входит в группу

        excluded = calculator_base._get_excluded_drugs_by_groups([drug1.id])
        assert excluded == {drug2.id - 1}

    def test_get_excluded_drugs_by_groups_empty_input(self, calculator_base):
        """При пустом списке препаратов возвращается пустое множество."""
        assert calculator_base._get_excluded_drugs_by_groups([]) == set()

    def test_analyze_potential_drugs(self, calculator_base, filled_db):
        """
        Проверка анализа потенциальных препаратов (которые можно добавить).

        Возвращаются списки препаратов, добавление которых приводит к классам
        "caution" (класс 2) или "incompatible" (класс 3).
        """
        three_drugs, three_side_effects = filled_db
        n_drug = [three_drugs[0].id, three_drugs[1].id]
        rangs_matrix, _, rangsum = calculator_base._build_rank_matrices(
            n_drug, 'rang_base'
        )
        id2side = {se.id - 1: se.se_name for se in three_side_effects}

        drugs_class_2, drugs_class_3 = calculator_base._analyze_potential_drugs(
            rangs_matrix, rangsum, n_drug, set(), id2side
        )

        # При заданных рангах третий препарат не вызывает проблем
        assert len(drugs_class_2) == 0
        assert len(drugs_class_3) == 0

    def test_analyze_potential_drugs_with_incompatible(self, calculator_base, filled_db):
        """Добавление препарата, приводящего к несовместимости."""
        three_drugs, three_side_effects = filled_db
        # Увеличим ранг у третьего препарата для первого эффекта
        DrugSideEffect.objects.filter(drug=three_drugs[2], side_effect=three_side_effects[0]).update(rang_base=1.0)
        n_drug = [three_drugs[0].id]
        rangs_matrix, _, rangsum = calculator_base._build_rank_matrices(n_drug, 'rang_base')
        id2side = {se.id - 1: se.se_name for se in three_side_effects}

        drugs_class_2, drugs_class_3 = calculator_base._analyze_potential_drugs(
            rangs_matrix, rangsum, n_drug, set(), id2side
        )
        assert len(drugs_class_3) == 1
        assert drugs_class_3[0]['drug_index'] == three_drugs[2].id - 1

    def test_get_se_from_drugs(self, calculator_base, filled_db):
        """
        Проверка получения побочных эффектов для каждого выбранного препарата.

        Возвращается список словарей с названием препарата и его эффектами.
        """
        three_drugs, _ = filled_db
        n_drug = [drug.id for drug in three_drugs[:2]]
        result = calculator_base._get_se_from_drugs(n_drug, set(), 'rang_base')

        assert len(result) == 2
        drug1_effects = result[0]['effects']
        assert len(drug1_effects) == 3
        ranks = [e['rank'] for e in drug1_effects]
        assert sorted(ranks, reverse=True) == [0.3, 0.06, 0.0]

    def test_get_se_from_drugs_empty(self, calculator_base):
        """При пустом списке препаратов возвращается пустой список."""
        assert calculator_base._get_se_from_drugs([], set(), 'rang_base') == []

    def test_get_drug_names_bulk(self, calculator_base, filled_db):
        """Проверка получения словаря имён препаратов по ID."""
        three_drugs, _ = filled_db
        ids = [drug.id for drug in three_drugs[:2]]
        names = calculator_base._get_drug_names_bulk(ids)
        assert len(names) == 2
        assert names[three_drugs[0].id] == three_drugs[0].drug_name

    def test_get_drug_names_bulk_empty(self, calculator_base):
        """При пустом списке возвращается пустой словарь."""
        assert calculator_base._get_drug_names_bulk([]) == {}

    def test_calculate_compatible(self, calculator_base):
        """
        Интеграционный тест: вычисление для совместимой комбинации.

        Ожидается классификация 'compatible'.
        """
        result = calculator_base.calculate('rang_base', [1, 2])
        assert result['compatibility_fortran'] == 'compatible'
        assert result['rank_iteractions'] == 0.35
        assert len(result['side_effects'][2]['effects']) == 0

    def test_calculate_caution(self, calculator_base, filled_db):
        """
        Тест для случая 'caution'.
        """
        three_drugs, three_side_effects = filled_db
        # Увеличим ранг, чтобы попасть в диапазон [0.5, 1.0)
        dse = DrugSideEffect.objects.get(drug=three_drugs[0], side_effect=three_side_effects[0])
        original = dse.rang_base
        dse.rang_base = 0.6
        dse.save()

        result = calculator_base.calculate('rang_base', [three_drugs[0].id])
        assert result['compatibility_fortran'] == 'caution'
        assert result['rank_iteractions'] == 0.6

        dse.rang_base = original
        dse.save()

    def test_calculate_incompatible(self, calculator_base, filled_db):
        """
        Интеграционный тест: вычисление для несовместимой комбинации.

        Увеличиваем ранг одного эффекта, чтобы получить класс 'incompatible'.
        """
        three_drugs, _ = filled_db
        drug_amiodarone = three_drugs[0]
        effect_hyperkal = SideEffect.objects.get(se_name="гиперкалиемия")
        dse = DrugSideEffect.objects.get(
            drug=drug_amiodarone, side_effect=effect_hyperkal
        )

        original = dse.rang_base
        dse.rang_base = 1.2
        dse.save()

        result = calculator_base.calculate(
            'rang_base', [drug_amiodarone.id, three_drugs[2].id]
        )
        assert result['compatibility_fortran'] == 'incompatible'

        # Восстановление исходного значения
        dse.rang_base = original
        dse.save()

    def test_calculate_with_gender_exclusion(self, calculator_base, three_side_effects):
        """
        Интеграционный тест: учёт пола при расчёте.

        Для мужчины исключается гипокалиемия (связана с женщинами),
        в результатах этого эффекта быть не должно.
        """
        se1 = SideEffect.objects.get(se_name="внутричерепное кровоизлияние")
        se2 = SideEffect.objects.get(se_name="гипокалиемия")
        se3 = SideEffect.objects.get(se_name="гиперкалиемия")

        SideEffectsGender.objects.get_or_create(side_effect=se1, gender='man')
        SideEffectsGender.objects.get_or_create(side_effect=se2, gender='woman')
        SideEffectsGender.objects.get_or_create(side_effect=se3, gender='man')

        result_man = calculator_base.calculate('rang_base', [1, 2], gender='man')
        assert result_man['compatibility_fortran'] == 'compatible'

        for se_list in result_man['side_effects']:
            for eff in se_list['effects']:
                assert eff['se_name'] != 'гипокалиемия'

    def test_calculate_with_canceling_normalization(self, calculator_with_canceling):
        """
        Интеграционный тест: расчёт с включённой нормализацией противоположных эффектов.

        Проверяем, что метод возвращает ожидаемую структуру ответа.
        """
        result = calculator_with_canceling.calculate('rang_base', [1, 3])
        assert 'compatibility_fortran' in result

    def test_calculate_with_cutoff(self, filled_db):
        """
        Интеграционный тест: расчёт с отсечкой нежизнеугрожающих эффектов.

        Увеличиваем ранг гипокалиемии (нежизнеугрожающий), ожидаем ограничение до 0.99.
        """
        se_hypokal = SideEffect.objects.get(id=2)
        se_hypokal.is_life_threatening = False
        se_hypokal.save()

        dse = DrugSideEffect.objects.get(drug_id=1, side_effect_id=2)
        original = dse.rang_base
        dse.rang_base = 1.5
        dse.save()

        calculator = FortranCalculator(
            normalize=False,
            cuttoff_not_life_threats_side_e=True
        )
        result = calculator.calculate('rang_base', [1])

        found = False
        for se_list in result['side_effects']:
            for eff in se_list['effects']:
                if eff['se_name'] == 'гипокалиемия':
                    assert eff['rank'] == 0.99
                    found = True
        assert found

        dse.rang_base = original
        dse.save()

    def test_calculate_with_recommendations(self, filled_db):
        """
        Интеграционный тест: формирование рекомендаций при несовместимости.

        Проверяет, что:
        - возвращается корректная структура рекомендаций,
        - среди рекомендаций есть группа с ожидаемым названием,
        - в рекомендациях указан проблемный препарат и альтернатива,
        - после замены ранг становится < 1.0.
        """
        three_drugs, three_side_effects = filled_db
        drug_main = three_drugs[0]
        drug_alt = three_drugs[2]

        # Очищаем существующие группы, чтобы изолировать тест
        drug_main.drug_groups.clear()
        drug_alt.drug_groups.clear()

        # Создаём тестовую группу и добавляем оба препарата
        group = DrugGroup.objects.create(dg_name="ТестоваяГруппа")
        drug_main.drug_groups.add(group)
        drug_alt.drug_groups.add(group)

        # Выбираем первый побочный эффект ("внутричерепное кровоизлияние")
        effect_hyperkal = three_side_effects[0]
        dse_main = DrugSideEffect.objects.get(drug=drug_main, side_effect=effect_hyperkal)
        dse_alt = DrugSideEffect.objects.get(drug=drug_alt, side_effect=effect_hyperkal)

        original_main = dse_main.rang_base
        original_alt = dse_alt.rang_base

        # Делаем комбинацию несовместимой
        dse_main.rang_base = 1.2
        dse_main.save()
        dse_alt.rang_base = 0.1
        dse_alt.save()

        calculator = FortranCalculator(normalize=False, cuttoff_not_life_threats_side_e=False)
        result = calculator.calculate('rang_base', [drug_main.id])

        assert result['compatibility_fortran'] == 'incompatible'
        assert 'rep_recommendations' in result

        recs = result['rep_recommendations']
        assert isinstance(recs, list)
        assert len(recs) > 0

        # Находим рекомендацию для созданной группы
        target_rec = None
        for rec in recs:
            if rec['group_name'] == group.dg_name:
                target_rec = rec
                break
        assert target_rec is not None, (
            f"Рекомендация для группы '{group.dg_name}' не найдена. "
            f"Найдены группы: {[r['group_name'] for r in recs]}"
        )

        drug_rec = target_rec['drugs'][0]
        assert drug_rec['drug_name'] == drug_main.drug_name
        assert 'replace_drugs' in drug_rec
        assert drug_alt.drug_name in drug_rec['replace_drugs']

        # Проверяем, что после замены совместимость становится допустимой (ранг < 1.0)
        rangs_matrix, _, _ = calculator._build_rank_matrices([drug_main.id], 'rang_base')
        rangsum_new = rangs_matrix[drug_alt.id - 1].copy()
        assert np.max(rangsum_new) < 1.0, "После замены максимальный ранг должен быть < 1.0"

        # Восстанавливаем исходные ранги
        dse_main.rang_base = original_main
        dse_main.save()
        dse_alt.rang_base = original_alt
        dse_alt.save()

    def test_prepare_combination_context_empty(self, calculator_base):
        """Проверка, что при пустых списках контекст формируется корректно."""
        context = calculator_base._prepare_combination_context([], [])
        assert context['combinations'][0]['drugs'] == []
        assert context['combinations'][1]['drugs'] == []

    def test_analyze_max_drug_contribution_no_effects(self, calculator_base):
        """Если нет несовместимых эффектов, возвращается пустой список."""
        recs = calculator_base._analyze_max_drug_contribution(
            [], np.array([]), [], np.array([]), {}
        )
        assert recs == {'rep_recommendations': []}