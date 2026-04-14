import pytest
import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path

from drugs.utils.loaders import ExcelLoader  # замените на реальный импорт
from drugs.models import Drug, SideEffect, SideEffectsGender, DrugSideEffect
from drugs.utils.custom_exception import IncorrectFile


pytestmark = pytest.mark.django_db


class TestExcelLoader:

    def test_check_excel_file_valid(self, valid_excel_file_3x3, tmp_path):
        """Проверка, что валидный файл не возвращает ошибок."""
        # Сохраняем временный файл на диск (фикстура возвращает SimpleUploadedFile)
        file_path = tmp_path / "test.xlsx"
        with open(file_path, "wb") as f:
            f.write(valid_excel_file_3x3.read())

        loader = ExcelLoader(import_path=str(file_path))
        errors = loader._check_excel_file()
        assert errors == [], f"Ожидался пустой список ошибок, получено: {errors}"

    def test_check_excel_file_missing_sheet(self, tmp_path):
        """Файл без обязательного листа должен вернуть ошибку."""
        df = pd.DataFrame({"A": [1, 2]})
        file_path = tmp_path / "bad.xlsx"
        df.to_excel(file_path, sheet_name="WrongSheet", index=False)

        loader = ExcelLoader(import_path=str(file_path))
        errors = loader._check_excel_file()
        assert any("Отсутствуют листы" in err for err in errors)

    def test_load_drugs_success(self, valid_excel_file_3x3, three_drugs, tmp_path):
        """_load_drugs не должен вызывать исключение, если все препараты из файла есть в БД."""
        file_path = tmp_path / "test.xlsx"
        with open(file_path, "wb") as f:
            f.write(valid_excel_file_3x3.read())

        loader = ExcelLoader(import_path=str(file_path))
        # Метод ничего не возвращает, но при ошибке бросает IncorrectFile
        loader._load_drugs()  # не должно быть исключения

    def test_load_drugs_unknown_drug(self, valid_excel_file_3x3, three_drugs, tmp_path):
        """Если в файле есть препарат, отсутствующий в БД, должно быть брошено IncorrectFile."""
        # Модифицируем файл: добавляем четвёртый неизвестный препарат
        file_path = tmp_path / "test_unknown.xlsx"
        # Читаем исходный Excel
        with pd.ExcelFile(valid_excel_file_3x3) as xlsx:
            drugs_df = pd.read_excel(xlsx, sheet_name="Drugs")
            effects_df = pd.read_excel(xlsx, sheet_name="Side_e")
            common_df = pd.read_excel(xlsx, sheet_name="Common", header=None)

        # Добавляем строку в Drugs
        new_drug = pd.DataFrame({"№": [4], "ЛС": ["неизвестный препарат"]})
        drugs_df = pd.concat([drugs_df, new_drug], ignore_index=True)

        # В Common нужно добавить столбец для нового препарата и заполнить ранги (например, нулями)
        # Текущий common_df имеет shape (5,5) – 3 препарата, 3 ПЭ + служебные строки/столбцы.
        # Расширим до 4 препаратов: добавляем столбец после существующих.
        # Проще пересоздать файл с новыми данными, но для теста достаточно изменить Drugs и оставить Common как есть.
        # Однако _load_ranks потом упадёт из-за несоответствия, но _load_drugs проверится раньше.
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            drugs_df.to_excel(writer, sheet_name="Drugs", index=False)
            effects_df.to_excel(writer, sheet_name="Side_e", index=False)
            common_df.to_excel(writer, sheet_name="Common", index=False, header=False)

        loader = ExcelLoader(import_path=str(file_path))
        with pytest.raises(IncorrectFile, match="обнаружены неизвестные препараты"):
            loader._load_drugs()

    def test_load_side_effects(self, valid_excel_file_3x3, three_side_effects, tmp_path):
        """Проверка создания/обновления побочных эффектов и их гендерных связей."""
        file_path = tmp_path / "test.xlsx"
        with open(file_path, "wb") as f:
            f.write(valid_excel_file_3x3.read())

        loader = ExcelLoader(import_path=str(file_path))
        loader._load_side_effects()

        # Проверяем, что все три эффекта существуют в БД
        for effect in three_side_effects:
            assert SideEffect.objects.filter(se_name=effect.se_name).exists()

        # Проверяем, что веса и флаги обновились в соответствии с файлом
        # В valid_excel_file_3x3 веса: 0.5,0.4,0.6, жизнеугрожающий: +,-,-
        effect1 = SideEffect.objects.get(se_name="внутричерепное кровоизлияние")
        assert effect1.weight == 0.5
        assert effect1.is_life_threatening is True

        effect2 = SideEffect.objects.get(se_name="гипокалиемия")
        assert effect2.weight == 0.4
        assert effect2.is_life_threatening is False

        # Проверяем гендерные связи (в фикстуре заданы: man, woman, man)
        genders = SideEffectsGender.objects.filter(side_effect=effect1)
        assert genders.count() == 1
        assert genders.first().gender == "man"

    def test_load_ranks(self, valid_excel_file_3x3, three_drugs, three_side_effects, tmp_path):
        """Проверка загрузки матрицы рангов для всех пар."""
        file_path = tmp_path / "test.xlsx"
        with open(file_path, "wb") as f:
            f.write(valid_excel_file_3x3.read())

        loader = ExcelLoader(import_path=str(file_path), transpose=True)
        result = loader._load_ranks()

        # Ожидаем 3 препарата * 3 ПЭ = 9 пар
        assert result["pairs_expected"] == 9
        assert result["pairs_loaded"] == 9

        # Проверяем конкретные ранги из матрицы rank_matrix в фикстуре
        # Матрица была:
        # [0.06, 0,   0.3]
        # [0.09, 0.2, 0.05]
        # [0.1,  0.2, 0.04]
        drug_amiodarone = Drug.objects.get(drug_name="амиодарон")
        drug_amlodipine = Drug.objects.get(drug_name="амлодипин+периндоприл")
        drug_apixaban = Drug.objects.get(drug_name="апиксабан")

        effect_ich = SideEffect.objects.get(se_name="внутричерепное кровоизлияние")
        effect_hypokal = SideEffect.objects.get(se_name="гипокалиемия")
        effect_hyperkal = SideEffect.objects.get(se_name="гиперкалиемия")

        # Ранг амиодарон + внутричерепное = 0.06
        rank = DrugSideEffect.objects.get(drug=drug_amiodarone, side_effect=effect_ich).rang_base
        assert rank == 0.06

        # амлодипин + гипокалиемия = 0.2
        rank = DrugSideEffect.objects.get(drug=drug_amlodipine, side_effect=effect_hypokal).rang_base
        assert rank == 0.2

        # апиксабан + гиперкалиемия = 0.04
        rank = DrugSideEffect.objects.get(drug=drug_apixaban, side_effect=effect_hyperkal).rang_base
        assert rank == 0.04

    def test_load_to_db_integration(self, valid_excel_file_3x3, three_drugs, three_side_effects, tmp_path):
        """Интеграционный тест: вызов load_to_db загружает всё без ошибок."""
        file_path = tmp_path / "test.xlsx"
        with open(file_path, "wb") as f:
            f.write(valid_excel_file_3x3.read())

        loader = ExcelLoader(import_path=str(file_path), transpose=True)
        loader.load_to_db()  # должен отработать без исключений

        # Проверяем, что ранги загружены
        assert DrugSideEffect.objects.count() == 9

        # Проверяем, что побочные эффекты обновлены
        assert SideEffect.objects.filter(se_name="внутричерепное кровоизлияние").exists()