import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
from drugs.models import Drug, DrugGroup, SideEffect, DrugSideEffect


# ===================== Фикстуры для 3×3 тестов =====================
@pytest.fixture
def drug_group():
    """Создаёт группу препаратов."""
    dg, _ = DrugGroup.objects.get_or_create(id=1, dg_name="Анальгетики")
    return dg


@pytest.fixture
def three_drugs(drug_group):
    """Создаёт три препарата в БД и возвращает список."""
    drugs_data = [
        {"id": 1, "drug_name": "амиодарон"},
        {"id": 2, "drug_name": "амлодипин+периндоприл"},
        {"id": 3, "drug_name": "апиксабан"}
    ]
    drugs = []
    for data in drugs_data:
        drug, _ = Drug.objects.get_or_create(**data)
        drug.drug_groups.add(drug_group)
        drugs.append(drug)
    return drugs

@pytest.fixture
def three_side_effects():
    """Создаёт три побочных эффекта в БД и возвращает список."""
    effects_data = [
        {"id": 1, "se_name": "внутричерепное кровоизлияние", "se_name_en": "intracranial hemorrhage", "weight": 0.5},
        {"id": 2, "se_name": "гипокалиемия", "se_name_en": "hypokalemia", "weight": 0.4},
        {"id": 3, "se_name": "гиперкалиемия", "se_name_en": "hyperkalemia", "weight": 0.6}
    ]
    effects = []
    for data in effects_data:
        effect, _ = SideEffect.objects.get_or_create(**data)
        effects.append(effect)
    return effects


@pytest.fixture
def valid_excel_file_3x3(tmp_path, three_drugs, three_side_effects):
    """
    Создаёт корректный Excel-файл с тремя препаратами и тремя побочками.
    Лист 'Common' соответствует реальной структуре:
    - Строка 1: пустые, пустые, номера препаратов (1,2,3)
    - Строка 2: пусто, 'ЛС/ПЭ', названия препаратов
    - Столбец A: номера ПЭ
    - Столбец B: названия ПЭ
    - Остальное: матрица рангов (строки = ПЭ, столбцы = ЛС)
    """
    drugs = three_drugs      # список из трёх Drug
    effects = three_side_effects  # список из трёх SideEffect

    # Лист Drugs
    drugs_df = pd.DataFrame({
        "№": [1, 2, 3],
        "ЛС": [d.drug_name for d in drugs]
    })

    # Лист Side_e
    effects_df = pd.DataFrame({
        "№": [1, 2, 3],
        "эффект": [e.se_name for e in effects],
        "эффект_en": [e.se_name_en for e in effects],
        "ранг": [e.weight for e in effects],
        "пол": ["man", "woman", "man"],
        "жизнеугрожающий": ["+", "-", "-"]
    })

    # Матрица рангов 3x3 (ПЭ по строкам, ЛС по столбцам)
    rank_matrix = [
        [0.06, 0,   0.3],
        [0.09, 0.2, 0.05],
        [0.1,  0.2, 0.04]
    ]

    # Построение DataFrame для листа Common
    # Количество строк = 2 (заголовки) + 3 (ПЭ) = 5
    # Количество столбцов = 2 (номера+названия) + 3 (препараты) = 5
    data = []

    # Строка 1: пустые, пустые, номера препаратов
    row1 = ["", "", "1", "2", "3"]
    data.append(row1)

    # Строка 2: пусто, "ЛС/ПЭ", названия препаратов
    row2 = ["", "ЛС/ПЭ"] + [drug.drug_name for drug in drugs]
    data.append(row2)

    # Строки 3-5: номера ПЭ, названия ПЭ, ранги
    for i, effect in enumerate(effects):
        row = [str(i+1), effect.se_name] + rank_matrix[i]
        data.append(row)

    # Создаём DataFrame без автоматических заголовков
    ranks_df = pd.DataFrame(data)

    # Запись в файл
    file_path = tmp_path / "test_import_3x3_transpose.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        drugs_df.to_excel(writer, sheet_name="Drugs", index=False)
        effects_df.to_excel(writer, sheet_name="Side_e", index=False)
        ranks_df.to_excel(writer, sheet_name="Common", index=False, header=False)

    with open(file_path, "rb") as f:
        return SimpleUploadedFile(
            "test_import_3x3.xlsx",
            f.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

@pytest.fixture
def setup_ranks(three_drugs, three_side_effects):
    """
    Заполняет таблицу DrugSideEffect тестовыми рангами.
    Матрица рангов: строки = препараты, столбцы = побочные эффекты.
    """
    # Матрица соответствует valid_excel_file_3x3
    rank_matrix = [
        [0.06, 0,   0.3],
        [0.09, 0.2, 0.05],
        [0.1,  0.2, 0.04]
    ]
    # Очистим старые связи, чтобы избежать дублей
    DrugSideEffect.objects.all().delete()
    for i, drug in enumerate(three_drugs):
        for j, effect in enumerate(three_side_effects):
            DrugSideEffect.objects.get_or_create(
                drug=drug,
                side_effect=effect,
                rang_base=rank_matrix[i][j],
                rang_f1=0.0, rang_f2=0.0, rang_freq=0.0, rang_m1=0.0, rang_m2=0.0,
                probability=rank_matrix[i][j]  # если нужно
            )
    return three_drugs, three_side_effects
