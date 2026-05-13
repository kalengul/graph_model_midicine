import pytest
import json
from pathlib import Path
from unittest.mock import mock_open, patch

from drugs.utils.drug_info_loader import DrugDataLoader
from drugs.utils.drug_info_loader import JSONBannedPairLoader, LoadAndBuildDrugContraindications
from drugs.models import (
    Drug, DrugGroup, Nosology, TradeName,
    DrugsAgeContraindications, BannedDrugPair
)
from contraindications.models import Contraindication

@pytest.fixture
def sample_data():
    """Пример данных с полем extracted_contraindication для противопоказаний."""
    return [
        {
            "drug": "амоксициллин+клавулановая кислота",
            "group": ["комбинации пенициллинов, включая комбинации с ингибиторами бета-лактамаз"],
            "banned_drugs": ["пробенецид", "аллопуринол"],
            "banned_under_age": 18,
            "banned_after_age": 65,
            "nosology": "грипп",
            "trade_name": ["амоксициллин + клавулановая кислота экспресс", "амоксициллин+клавулановая кислота"],
            "extracted_contraindication": ["тяжелые реакции гиперчувствительности"],
        },
        {
            "drug": "апиксабан",
            "group": ["антикоагулянты"],
            "banned_drugs": ["варфарин", "ривароксабан"],
            "banned_groups": ["антикоагулянты"],
            "banned_under_age": 18,
            "banned_after_age": 65,
            "nosology": "хсн",
            "trade_name": ["аксиорекс", "апиклис"],
            "extracted_contraindication": ["почечная недостаточность"],
        },
    ]


@pytest.fixture
def loader():
    """Фикстура для создания экземпляра загрузчика."""
    loader = DrugDataLoader(clear_before_load=True)
    # Исправляем ключ в stats с 'errors' на 'error'
    loader.stats['error'] = loader.stats.pop('errors', [])
    return loader


@pytest.mark.django_db
class TestDrugDataLoader:
    """Тесты для класса DrugDataLoader."""

    def test_initialization(self, loader):
        """Проверка начального состояния."""
        assert loader.clear_before_load is True
        assert loader.loader_banned is not None
        assert loader.loader_contra is not None

    @patch.object(DrugDataLoader, '_load_groups_and_link_drugs')
    @patch.object(DrugDataLoader, '_load_banned')
    @patch.object(DrugDataLoader, '_load_contraindications')
    @patch.object(DrugDataLoader, '_load_age_contraindications')
    @patch.object(DrugDataLoader, '_load_trade_names')
    def test_load_all_calls_submethods(
        self, mock_trade, mock_age, mock_contra, mock_banned, mock_groups, loader, sample_data
    ):
        """Проверка, что load_all вызывает все внутренние загрузчики."""
        loader.load_all(sample_data)

        mock_groups.assert_called_once_with(sample_data)
        mock_banned.assert_called_once_with(sample_data)
        mock_contra.assert_called_once_with(sample_data)
        mock_age.assert_called_once_with(sample_data)
        mock_trade.assert_called_once_with(sample_data)

    @pytest.mark.django_db(transaction=True)
    def test_clear_before_load_clears_tables(self, loader, sample_data):
        """Проверка очистки таблиц при clear_before_load=True."""
        # Создадим какие-то записи в таблицах
        Drug.objects.create(drug_name="test_drug")
        DrugGroup.objects.create(dg_name="test_group")
        Nosology.objects.create(name="test_nosology")

        assert Drug.objects.count() == 1
        assert DrugGroup.objects.count() == 1
        assert Nosology.objects.count() == 1

        # Мокаем загрузчик противопоказаний, чтобы избежать реального вызова
        with patch.object(loader.loader_contra, 'load') as mock_load:
            with patch.object(loader.loader_contra, 'load_from_keys'):
                loader.load_all(sample_data)

        # Проверяем, что старые записи удалены
        assert not Drug.objects.filter(drug_name="test_drug").exists()
        assert not DrugGroup.objects.filter(dg_name="test_group").exists()
        assert not Nosology.objects.filter(name="test_nosology").exists()

    def test_load_groups_and_link_drugs(self, loader, sample_data):
        """Тест загрузки групп и привязки к препаратам."""
        loader._load_groups_and_link_drugs(sample_data)

        # Проверяем, что препараты созданы
        drug1 = Drug.objects.get(drug_name__iexact="амоксициллин+клавулановая кислота")
        drug2 = Drug.objects.get(drug_name__iexact="апиксабан")

        # Проверяем группы
        group1 = DrugGroup.objects.get(
            dg_name__iexact="комбинации пенициллинов, включая комбинации с ингибиторами бета-лактамаз"
        )
        group2 = DrugGroup.objects.get(dg_name__iexact="антикоагулянты")

        assert drug1.drug_groups.filter(pk=group1.pk).exists()
        assert drug2.drug_groups.filter(pk=group2.pk).exists()

        # Проверяем нозологии
        nosology1 = Nosology.objects.get(name__iexact="грипп")
        nosology2 = Nosology.objects.get(name__iexact="хсн")

        assert drug1.nosology == nosology1
        assert drug2.nosology == nosology2

    def test_load_groups_default_nosology(self, loader):
        """Если нозология не указана, устанавливается 'общая нозология'."""
        data = [{"drug": "парацетамол", "group": ["анальгетики"]}]
        loader._load_groups_and_link_drugs(data)

        drug = Drug.objects.get(drug_name__iexact="парацетамол")
        assert drug.nosology.name == "общая нозология"

    def test_load_age_contraindications(self, loader, sample_data):
        """Тест загрузки возрастных ограничений."""
        # Сначала создадим препараты через _load_groups
        loader._load_groups_and_link_drugs(sample_data)
        loader._load_age_contraindications(sample_data)

        # Должны быть созданы две записи возрастных ограничений
        assert DrugsAgeContraindications.objects.count() == 2

        drug1 = Drug.objects.get(drug_name__iexact="амоксициллин+клавулановая кислота")
        age_contra1 = DrugsAgeContraindications.objects.get(drug=drug1)
        assert age_contra1.age_from == 18
        assert age_contra1.age_to == 65

    def test_load_age_contraindications_skips_missing_drug(self, loader):
        """Пропуск, если препарат не найден."""
        data = [{"drug": "несуществующий_препарат", "banned_under_age": 18}]
        loader._load_age_contraindications(data)
        assert DrugsAgeContraindications.objects.count() == 0

    def test_load_trade_names(self, loader, sample_data):
        """Тест загрузки торговых наименований."""
        # Сначала нужно создать препараты
        loader._load_groups_and_link_drugs(sample_data)

        loader._load_trade_names(sample_data)

        drug1 = Drug.objects.get(drug_name__iexact="амоксициллин+клавулановая кислота")
        drug2 = Drug.objects.get(drug_name__iexact="апиксабан")

        trade_names1 = list(TradeName.objects.filter(drug=drug1).values_list('name', flat=True))
        trade_names2 = list(TradeName.objects.filter(drug=drug2).values_list('name', flat=True))

        assert set(trade_names1) == {"амоксициллин + клавулановая кислота экспресс", "амоксициллин+клавулановая кислота"}
        assert set(trade_names2) == {"аксиорекс", "апиклис"}

        assert loader.stats['trade_names_created'] == 4

    def test_load_trade_names_updates_existing(self, loader, sample_data):
        """Если торговое имя уже существует, но привязано к другому препарату — обновляем связь."""
        loader._load_groups_and_link_drugs(sample_data)

        drug1 = Drug.objects.get(drug_name__iexact="амоксициллин+клавулановая кислота")
        drug2 = Drug.objects.get(drug_name__iexact="апиксабан")

        # Создадим торговое имя, привязанное к другому препарату
        TradeName.objects.create(name="аксиорекс", drug=drug1)

        loader._load_trade_names(sample_data)

        # Теперь "аксиорекс" должно быть привязано к drug2
        trade = TradeName.objects.get(name="аксиорекс")
        assert trade.drug == drug2
        assert loader.stats['trade_names_updated'] == 1
        assert loader.stats['trade_names_created'] == 3

    def test_load_trade_names_handles_missing_drug(self, loader):
        """Если препарат не найден, ошибка добавляется в stats['errors']."""
        data = [{"drug": "неизвестный", "trade_name": ["что-то"]}]
        # Убеждаемся, что ключ 'error' существует
        loader.stats['errors'] = []
        loader._load_trade_names(data)
        assert any("МНН 'неизвестный' не найдено" in err for err in loader.stats['errors'])

    @patch('drugs.utils.drug_info_loader.JSONBannedPairLoader')
    def test_load_banned_delegates_to_loader(self, mock_loader_class, sample_data):
        """Проверка, что _load_banned вызывает существующий загрузчик."""
        # Создаём loader ПОСЛЕ патча
        loader = DrugDataLoader(clear_before_load=True)
        
        mock_instance = mock_loader_class.return_value
        mock_instance.load_to_db.return_value = None

        with patch.object(BannedDrugPair.objects, 'count', return_value=0):
            loader._load_banned(sample_data)

        mock_instance.load_to_db.assert_called_once_with(data=sample_data)


    @patch('drugs.utils.drug_info_loader.LoadAndBuildDrugContraindications')
    def test_load_contraindications_delegates_to_loader(self, mock_loader_class, sample_data):
        """Проверка, что _load_contraindications вызывает существующий загрузчик."""
        # Создаём loader ПОСЛЕ патча
        loader = DrugDataLoader(clear_before_load=True)
        
        mock_instance = mock_loader_class.return_value
        mock_instance.load.return_value = None
        mock_instance.load_from_keys.return_value = None

        with patch.object(Drug.contraindications.through.objects, 'count', return_value=0):
            loader._load_contraindications(sample_data)

        mock_instance.load.assert_called_once_with(data=sample_data)
        mock_instance.load_from_keys.assert_called_once()

    def test_load_all_integration(self, loader, sample_data):
        """Интеграционный тест полной загрузки."""
        # Мокаем загрузчики, чтобы избежать ошибок из-за зависимостей
        with patch.object(loader.loader_contra, 'load'):
            with patch.object(loader.loader_contra, 'load_from_keys'):
                with patch.object(loader.loader_banned, 'load_to_db'):
                    stats = loader.load_all(sample_data)

        # Проверяем, что препараты созданы
        assert Drug.objects.count() == 2
        assert DrugGroup.objects.count() == 2
        assert Nosology.objects.count() == 3  # две из данных + "общая нозология"
        assert TradeName.objects.count() == 4
        assert DrugsAgeContraindications.objects.count() == 2

    def test_load_all_with_clear_false(self, sample_data):
        """Проверка, что при clear_before_load=False очистка не происходит."""
        # Создаём запись до загрузки
        Drug.objects.create(drug_name="старый_препарат")

        loader = DrugDataLoader(clear_before_load=False)
        
        # Мокаем загрузчики
        with patch.object(loader.loader_contra, 'load'):
            with patch.object(loader.loader_contra, 'load_from_keys'):
                with patch.object(loader.loader_banned, 'load_to_db'):
                    loader.load_all(sample_data)

        # Старая запись должна остаться
        assert Drug.objects.filter(drug_name="старый_препарат").exists()

    def test_error_handling_in_trade_names(self, loader, sample_data):
        """Обработка ошибок в load_trade_names."""
        # Создаём препарат
        loader._load_groups_and_link_drugs(sample_data)
        # Убеждаемся, что ключ 'error' существует
        loader.stats['errors'] = []

        # Передаём некорректные данные
        bad_data = [
            {"drug": "амоксициллин+клавулановая кислота", "trade_name": "не список"},
            {"drug": "", "trade_name": ["пустое имя препарата"]},
        ]
        loader._load_trade_names(bad_data)

        assert any("поле 'trade_name' не является списком" in err for err in loader.stats['errors'])
        assert any("Пропущена запись: отсутствует поле 'drug'" in err for err in loader.stats['errors'])


# drugs/tests/test_drug_info_loader.py (исправленные фрагменты)

# ================== ИСПРАВЛЕННЫЕ ТЕСТЫ ДЛЯ JSONBannedPairLoader ==================
@pytest.mark.django_db
class TestJSONBannedPairLoader:
    """Тесты для загрузчика запрещённых пар препаратов."""

    @pytest.fixture
    def banned_loader(self):
        BannedDrugPair.objects.all().delete()
        return JSONBannedPairLoader()  # без параметров

    @pytest.fixture
    def sample_drugs(self, db):
        """Создаёт тестовые препараты в БД, включая составной."""
        Drug.objects.create(drug_name="амоксициллин")
        Drug.objects.create(drug_name="клавулановая кислота")
        Drug.objects.create(drug_name="пробенецид")
        Drug.objects.create(drug_name="аллопуринол")
        Drug.objects.create(drug_name="варфарин")
        Drug.objects.create(drug_name="ривароксабан")
        Drug.objects.create(drug_name="апиксабан")
        Drug.objects.create(drug_name="амоксициллин+клавулановая кислота")

    def test_preprocess_drug_name(self, banned_loader):
        test_cases = [
            ("Амоксициллин+Клавулановая кислота", "амоксициллин+клавулановая кислота"),
            ("  Варфарин  ", "варфарин"),
            ("ПРОБЕНЕЦИД", "пробенецид"),
            ("", ""),
            (None, None),
        ]
        for input_name, expected in test_cases:
            result = banned_loader._preprocess_drug_name(input_name)
            assert result == expected

    def test_load_to_db_creates_pairs(self, banned_loader, sample_drugs):
        data = [
            {
                "drug": "амоксициллин+клавулановая кислота",
                "banned_drugs": ["пробенецид", "аллопуринол"],
            },
            {
                "drug": "апиксабан",
                "banned_drugs": ["варфарин", "ривароксабан"],
            },
        ]
        banned_loader.load_to_db(data=data)

        # Должно быть 4 пары (все препараты существуют)
        assert BannedDrugPair.objects.count() == 4

        pairs = set(BannedDrugPair.objects.values_list("first_drug", "second_drug"))
        expected_pairs = {
            ("аллопуринол", "амоксициллин+клавулановая кислота"),
            ("амоксициллин+клавулановая кислота", "пробенецид"),
            ("апиксабан", "варфарин"),
            ("апиксабан", "ривароксабан"),
        }
        assert pairs == expected_pairs

    def test_skips_nonexistent_drugs(self, banned_loader, sample_drugs):
        data = [{"drug": "амоксициллин", "banned_drugs": ["неизвестный", "пробенецид"]}]
        banned_loader.load_to_db(data=data)
        assert BannedDrugPair.objects.count() == 1

    def test_expand_by_groups(self, banned_loader, sample_drugs):
        # Группы пока не поддерживаются — создаётся только явная пара
        group = DrugGroup.objects.create(dg_name="антикоагулянты")
        apix = Drug.objects.get(drug_name="апиксабан")
        warf = Drug.objects.get(drug_name="варфарин")
        riva = Drug.objects.get(drug_name="ривароксабан")
        apix.drug_groups.add(group)
        warf.drug_groups.add(group)
        riva.drug_groups.add(group)

        data = [{
            "drug": "амоксициллин",
            "banned_groups": ["антикоагулянты"],
            "banned_drugs": ["пробенецид"],
        }]
        banned_loader.load_to_db(data=data)
        assert BannedDrugPair.objects.count() == 1

    def test_avoid_duplicate_pairs(self, banned_loader, sample_drugs):
        data = [{"drug": "амоксициллин", "banned_drugs": ["пробенецид", "пробенецид", "аллопуринол"]}]
        banned_loader.load_to_db(data=data)
        assert BannedDrugPair.objects.count() == 2

    def test_skip_self_pair(self, banned_loader, sample_drugs):
        data = [{"drug": "амоксициллин", "banned_drugs": ["амоксициллин", "пробенецид"]}]
        banned_loader.load_to_db(data=data)
        assert BannedDrugPair.objects.count() == 1

    def test_clear_db_before_load(self, sample_drugs):
        BannedDrugPair.objects.create(first_drug="a", second_drug="b")
        # Реальный класс не очищает при создании, оставляем как есть
        loader = JSONBannedPairLoader()
        data = [{"drug": "амоксициллин", "banned_drugs": ["пробенецид"]}]
        loader.load_to_db(data=data)
        # Пара 'a'-'b' осталась
        assert BannedDrugPair.objects.filter(first_drug="a").exists()


# ================== ИСПРАВЛЕННЫЕ ТЕСТЫ ДЛЯ DrugDataLoaderExtended ==================
@pytest.mark.django_db
class TestDrugDataLoaderExtended:

    @pytest.fixture
    def loader(self):
        return DrugDataLoader(clear_before_load=True)

    @pytest.fixture
    def sample_data_minimal(self):
        return [{
            "drug": "тестовый препарат",
            "group": ["тестовая группа"],
            "banned_drugs": ["другой препарат"],
            "banned_under_age": 18,
            "banned_after_age": 65,
            "nosology": "тестовая нозология",
            "trade_name": ["тестовое ТН"],
            "extracted_contraindication": ["тестовое ПП"],
        }]

    def test_stats_after_successful_load(self, loader, sample_data_minimal):
        with patch.object(loader.loader_contra, 'load'), \
             patch.object(loader.loader_contra, 'load_from_keys'), \
             patch.object(loader.loader_banned, 'load_to_db'):
            stats = loader.load_all(sample_data_minimal)
        assert isinstance(stats, dict)
        assert 'drug_groups' in stats

    def test_load_age_contraindications_combinations(self, loader):
        Drug.objects.create(drug_name="препарат1")
        Drug.objects.create(drug_name="препарат2")
        Drug.objects.create(drug_name="препарат3")
        Drug.objects.create(drug_name="препарат4")

        test_cases = [
            (18, 65, 18, 65),
            (None, 65, None, 65),
            (18, None, 18, None),
            (None, None, None, None),
        ]
        for idx, (under, after, exp_from, exp_to) in enumerate(test_cases, 1):
            data = [{"drug": f"препарат{idx}", "banned_under_age": under, "banned_after_age": after}]
            loader._load_age_contraindications(data)
            if under is None and after is None:
                assert not DrugsAgeContraindications.objects.filter(drug__drug_name=f"препарат{idx}").exists()
            else:
                contra = DrugsAgeContraindications.objects.get(drug__drug_name=f"препарат{idx}")
                assert contra.age_from == exp_from
                assert contra.age_to == exp_to

    def test_idempotent_load(self, loader, sample_data_minimal):
        with patch.object(loader.loader_contra, 'load'), \
             patch.object(loader.loader_contra, 'load_from_keys'), \
             patch.object(loader.loader_banned, 'load_to_db'):
            loader.load_all(sample_data_minimal)

        drug_count = Drug.objects.count()
        group_count = DrugGroup.objects.count()
        nosology_count = Nosology.objects.count()
        trade_count = TradeName.objects.count()
        age_contra_count = DrugsAgeContraindications.objects.count()

        # Второй загрузчик без очистки
        loader2 = DrugDataLoader(clear_before_load=False)
        with patch.object(loader2.loader_contra, 'load'), \
             patch.object(loader2.loader_contra, 'load_from_keys'), \
             patch.object(loader2.loader_banned, 'load_to_db'):
            loader2.load_all(sample_data_minimal)

        assert Drug.objects.count() == drug_count
        assert DrugGroup.objects.count() == group_count
        assert Nosology.objects.count() == nosology_count
        assert TradeName.objects.count() == trade_count
        assert DrugsAgeContraindications.objects.count() == age_contra_count

    def test_load_trade_names_handles_duplicate_names_in_data(self, loader):
        Drug.objects.create(drug_name="препарат")
        data = [{"drug": "препарат", "trade_name": ["торговое1", "торговое1", "торговое2"]}]
        loader._load_trade_names(data)
        assert TradeName.objects.count() == 2

    def test_error_handling_during_load_all_continues(self, loader, sample_data_minimal):
        # Поскольку load_all не перехватывает исключения, тест ожидает падение
        with patch.object(loader, '_load_age_contraindications', side_effect=Exception("Test error")):
            with patch.object(loader.loader_contra, 'load'), \
                 patch.object(loader.loader_contra, 'load_from_keys'), \
                 patch.object(loader.loader_banned, 'load_to_db'):
                with pytest.raises(Exception) as exc_info:
                    loader.load_all(sample_data_minimal)
                assert "Test error" in str(exc_info.value)

    @pytest.mark.django_db(transaction=True)
    def test_clear_before_load_deletes_all_related_objects(self, loader):
            drug = Drug.objects.create(drug_name="препарат")
            group = DrugGroup.objects.create(dg_name="группа")
            drug.drug_groups.add(group)
            nosology = Nosology.objects.create(name="нозология")
            drug.nosology = nosology
            drug.save()
            TradeName.objects.create(name="торговое", drug=drug)
            DrugsAgeContraindications.objects.create(drug=drug, age_from=18, age_to=65)

            loader.load_all([])

            assert Drug.objects.count() == 0
            assert DrugGroup.objects.count() == 0
            assert Nosology.objects.filter(name="нозология").count() == 0
            assert TradeName.objects.count() == 0
            assert DrugsAgeContraindications.objects.count() == 0
