"""Тесты API приложения drugs."""

import pytest
import json

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


from drugs.models import (
    Drug,
    DrugGroup,
    Nosology,
    TradeName,
    BannedDrugPair
)
from side_effects.models import SideEffect

FORMAT = "json"
DATA = "data"
RESULT = "result"


@pytest.fixture
def client(db):
    user = User.objects.create_user(username="testuser", password="testpass")
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")
    return client


@pytest.fixture
def drug_group():
    return DrugGroup.objects.create(dg_name="Группа ЛС")


@pytest.fixture
def nosology():
    return Nosology.objects.create(name="Нозология")


@pytest.fixture
def drug(drug_group, nosology):
    instance = Drug.objects.create(
        drug_name="ЛС",
        nosology=nosology,
    )
    instance.drug_groups.add(drug_group)
    return instance


# ---------------------------------------------------------------------------
# DrugGroupAPI
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_add_drug_group_api(client):
    """Проверка добавления группы ЛС."""
    payload = {"dg_name": "диуретики"}

    response = client.post("/api/v1/DrugGroup/", payload, format=FORMAT)

    assert response.status_code == status.HTTP_200_OK
    assert DrugGroup.objects.filter(dg_name="диуретики").exists()
    assert response.data[DATA] == {
        "id": 1,
        "dg_name": "диуретики",
    }
    assert response.data[RESULT]["status"] == status.HTTP_200_OK


@pytest.mark.django_db
def test_add_duplicate_drug_group_api(client):
    """Повторное добавление группы возвращает 400."""
    DrugGroup.objects.create(dg_name="диуретики")

    response = client.post(
        "/api/v1/DrugGroup/",
        {"dg_name": "Диуретики"},
        format=FORMAT,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert DrugGroup.objects.count() == 1
    assert "уже существует" in response.data[RESULT]["message"]


@pytest.mark.django_db
def test_get_drug_group_list_api(client):
    """Проверка получения списка групп ЛС."""
    DrugGroup.objects.create(dg_name="Группа ЛС 1")
    DrugGroup.objects.create(dg_name="Группа ЛС 2")

    response = client.get("/api/v1/DrugGroup/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data[DATA]) == 2
    assert set(response.data[DATA][0].keys()) == {"id", "dg_name"}


@pytest.mark.django_db
def test_get_drug_group_detail_api(client):
    """Проверка получения одной группы ЛС."""
    group = DrugGroup.objects.create(dg_name="Группа ЛС")

    response = client.get(
        "/api/v1/DrugGroup/",
        {"dg_id": group.id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[DATA] == {
        "id": group.id,
        "dg_name": "Группа ЛС",
    }


@pytest.mark.django_db
def test_get_missing_drug_group_api(client):
    """Запрос отсутствующей группы возвращает 404."""
    response = client.get("/api/v1/DrugGroup/", {"dg_id": 999})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data[RESULT]["message"] == "Группа ЛС не найдена"


@pytest.mark.django_db
def test_delete_drug_group_api(client):
    """Проверка удаления группы через endpoint."""
    group = DrugGroup.objects.create(dg_name="Группа ЛС")

    response = client.delete(
        "/api/v1/DrugGroup/",
        {"dg_id": group.id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert not DrugGroup.objects.filter(pk=group.id).exists()
    assert response.data[DATA] == {}


@pytest.mark.django_db
def test_delete_missing_drug_group_api(client):
    """Удаление отсутствующей группы возвращает 400."""
    response = client.delete("/api/v1/DrugGroup/", {"dg_id": 999})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[RESULT]["message"] == (
        "Ошибка определения удаляемого объекта"
    )


# ---------------------------------------------------------------------------
# DrugAPI
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_add_drug_api(client, drug_group):
    """Проверка добавления ЛС с группой и побочным эффектом."""
    side_effect = SideEffect.objects.create(se_name="ПД")

    payload = {
        "drug_name": "Новое ЛС",
        "dg_ids": [drug_group.id],
        "side_effects": [
            {
                "se_id": side_effect.id,
                "rank": 0.8,
            }
        ],
    }

    response = client.post("/api/v1/Drug/", payload, format=FORMAT)

    assert response.status_code == status.HTTP_200_OK
    assert Drug.objects.count() == 1
    assert response.data[DATA]["drug_name"] == "Новое ЛС"

    created_drug = Drug.objects.get(drug_name="Новое ЛС")
    assert list(created_drug.drug_groups.values_list("id", flat=True)) == [
        drug_group.id
    ]

    relation = created_drug.side_effects.through.objects.get(
        drug=created_drug,
        side_effect=side_effect,
    )
    assert relation.probability == 0.8


@pytest.mark.django_db
def test_add_drug_api_with_nosology(client, drug_group, nosology):
    """Проверка создания ЛС с нозологией."""
    payload = {
        "drug_name": "ЛС с нозологией",
        "dg_ids": [drug_group.id],
        "nosology_id": nosology.id,
    }

    response = client.post("/api/v1/Drug/", payload, format=FORMAT)

    assert response.status_code == status.HTTP_200_OK

    created_drug = Drug.objects.get(drug_name="ЛС с нозологией")
    assert created_drug.nosology_id == nosology.id
    assert response.data[DATA] == {
        "id": created_drug.id,
        "drug_name": "ЛС с нозологией",
    }


@pytest.mark.django_db
def test_add_duplicate_drug_api(client):
    """Повторное добавление ЛС возвращает 400."""
    Drug.objects.create(drug_name="ЛС")

    response = client.post(
        "/api/v1/Drug/",
        {"drug_name": "лс"},
        format=FORMAT,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Drug.objects.count() == 1
    assert "уже существует" in response.data[RESULT]["message"]


@pytest.mark.django_db
def test_get_drug_list_api(client, drug, drug_group, nosology):
    """Проверка актуального формата списка ЛС."""
    TradeName.objects.create(name="Торговое ЛС", drug=drug)

    response = client.get("/api/v1/Drug/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data[DATA]) == 1

    item = response.data[DATA][0]
    assert set(item) == {
        "id",
        "drug_name",
        "dg_id",
        "nosology_id",
        "trade_ids",
    }
    assert item["id"] == drug.id
    assert item["drug_name"] == "ЛС"
    assert item["dg_id"] == [drug_group.id]
    assert item["nosology_id"] == nosology.id
    assert len(item["trade_ids"]) == 1


@pytest.mark.django_db
def test_get_drug_detail_api(client, drug, drug_group, nosology):
    """Проверка получения одного ЛС в новом формате."""
    trade_name = TradeName.objects.create(name="Торговое ЛС", drug=drug)

    response = client.get(
        "/api/v1/Drug/",
        {"drug_id": drug.id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[DATA] == {
        "id": drug.id,
        "drug_name": "ЛС",
        "dg_id": [drug_group.id],
        "nosology_id": nosology.id,
        "trade_ids": [trade_name.id],
    }


@pytest.mark.django_db
def test_get_missing_drug_api(client):
    """Запрос отсутствующего ЛС возвращает 404."""
    response = client.get("/api/v1/Drug/", {"drug_id": 999})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data[RESULT]["message"] == (
        "Лекарственное средство не найдено"
    )


@pytest.mark.django_db
def test_delete_drug_api(client, drug):
    """Проверка удаления ЛС через актуальный endpoint."""
    drug_id = drug.id

    response = client.delete(
        "/api/v1/Drug/",
        {"drug_id": drug_id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert not Drug.objects.filter(pk=drug_id).exists()
    assert response.data[DATA] == {}


@pytest.mark.django_db
def test_delete_missing_drug_api(client):
    """Удаление отсутствующего ЛС возвращает 400."""
    response = client.delete("/api/v1/Drug/", {"drug_id": 999})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[RESULT]["message"] == (
        "Ошибка определения удаляемого ЛС"
    )


# ---------------------------------------------------------------------------
# SideEffectAPI
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_add_side_effect_api(client, drug):
    """Проверка добавления ПД и связи с ЛС."""
    payload = {
        "se_name": "почечная недостаточность",
        "side_effects": [
            {
                "drug_id": drug.id,
                "rank": 0.8,
            }
        ],
    }

    response = client.post(
        "/api/v1/SideEffect/",
        payload,
        format=FORMAT,
    )

    assert response.status_code == status.HTTP_200_OK
    assert SideEffect.objects.count() == 1
    assert response.data[DATA]["se_name"] == "почечная недостаточность"

    side_effect = SideEffect.objects.get()
    relation = drug.side_effects.through.objects.get(
        drug=drug,
        side_effect=side_effect,
    )
    assert relation.probability == 0.8


@pytest.mark.django_db
def test_add_side_effect_without_explicit_links_api(client, drug):
    """Без side_effects ПД связывается со всеми существующими ЛС."""
    response = client.post(
        "/api/v1/SideEffect/",
        {"se_name": "ПД"},
        format=FORMAT,
    )

    assert response.status_code == status.HTTP_200_OK

    side_effect = SideEffect.objects.get()
    assert drug.side_effects.filter(pk=side_effect.id).exists()


@pytest.mark.django_db
def test_add_duplicate_side_effect_api(client):
    """Повторное добавление ПД возвращает 400."""
    SideEffect.objects.create(se_name="ПД")

    response = client.post(
        "/api/v1/SideEffect/",
        {"se_name": "пд"},
        format=FORMAT,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert SideEffect.objects.count() == 1
    assert "уже существует" in response.data[RESULT]["message"]


@pytest.mark.django_db
def test_get_side_effect_list_api(client):
    """Проверка получения списка ПД."""
    SideEffect.objects.create(se_name="ПД1")
    SideEffect.objects.create(se_name="ПД2")

    response = client.get("/api/v1/SideEffect/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data[DATA]) == 2
    assert set(response.data[DATA][0]) == {"id", "se_name"}


@pytest.mark.django_db
def test_get_side_effect_detail_api(client):
    """Проверка получения одного ПД."""
    side_effect = SideEffect.objects.create(se_name="ПД1")

    response = client.get(
        "/api/v1/SideEffect/",
        {"se_id": side_effect.id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[DATA] == {
        "id": side_effect.id,
        "se_name": "ПД1",
    }


@pytest.mark.django_db
def test_get_missing_side_effect_api(client):
    """Запрос отсутствующего ПД возвращает 404."""
    response = client.get("/api/v1/SideEffect/", {"se_id": 999})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data[RESULT]["message"] == "Побочный эффект не найден"


@pytest.mark.django_db
def test_delete_side_effect_api(client):
    """Проверка удаления ПД через актуальный endpoint."""
    side_effect = SideEffect.objects.create(se_name="ПД1")

    response = client.delete(
        "/api/v1/SideEffect/",
        {"se_id": side_effect.id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert not SideEffect.objects.filter(pk=side_effect.id).exists()
    assert response.data[DATA] == {}


@pytest.mark.django_db
def test_delete_missing_side_effect_api(client):
    """Удаление отсутствующего ПД возвращает 400."""
    response = client.delete(
        "/api/v1/SideEffect/",
        {"se_id": 999},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[RESULT]["message"] == (
        "Ошибка определения удаляемого объекта"
    )


# ---------------------------------------------------------------------------
# TradeNameView
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_trade_names_api(client, drug):
    """Получение торговых названий препарата."""
    TradeName.objects.create(name="Торговое 1", drug=drug)
    TradeName.objects.create(name="Торговое 2", drug=drug)

    response = client.get(
        "/api/v1/TradeName/",
        {"drug_id": drug.id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[DATA] == {
        "drug_id": drug.id,
        "drug_name": "ЛС",
        "trade_names": ["Торговое 1", "Торговое 2"],
    }


@pytest.mark.django_db
def test_get_trade_names_without_drug_id_api(client):
    """Без drug_id endpoint возвращает 400."""
    response = client.get("/api/v1/TradeName/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[RESULT]["message"] == "Параметр drug_id обязателен"


@pytest.mark.django_db
def test_get_trade_names_for_missing_drug_api(client):
    """Для отсутствующего препарата возвращается 404."""
    response = client.get(
        "/api/v1/TradeName/",
        {"drug_id": 999},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data[RESULT]["message"] == (
        "Лекарственное средство не найдено"
    )


# ---------------------------------------------------------------------------
# DrugTradeSearchView
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_search_drugs_by_drug_name_api(client, drug):
    """Поиск ЛС по началу МНН."""
    TradeName.objects.create(name="Торговое ЛС", drug=drug)

    response = client.get(
        "/api/v1/search-drugs/",
        {"q": "ЛС"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[DATA]["query"] == "ЛС"
    assert response.data[DATA]["count"] == 1

    item = response.data[DATA]["results"][0]
    assert item["id"] == drug.id
    assert item["drug_name"] == "ЛС"
    assert item["dg_id"] == [drug.drug_groups.first().id]
    assert item["nosology_id"] == drug.nosology_id
    assert item["trade_names"] == []


@pytest.mark.django_db
def test_search_drugs_by_trade_name_api(client, drug):
    """Поиск ЛС по началу торгового названия."""
    trade_name = TradeName.objects.create(
        name="Аспирин-ЛС",
        drug=drug,
    )
    TradeName.objects.create(name="Другое название", drug=drug)

    response = client.get(
        "/api/v1/search-drugs/",
        {"q": "аспирин"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[DATA]["query"] == "аспирин"
    assert response.data[DATA]["count"] == 1

    item = response.data[DATA]["results"][0]
    assert item["id"] == drug.id
    assert item["drug_name"] == "ЛС"
    assert item["trade_names"] == [
        {"id": trade_name.id, "name": "Аспирин-ЛС"}
    ]


@pytest.mark.django_db
def test_search_drugs_prioritizes_mnn_match_api(client, drug_group):
    """ЛС, совпавшие по МНН, идут раньше совпавших по торговому названию."""
    first = Drug.objects.create(drug_name="Аспирин")
    first.drug_groups.add(drug_group)

    second = Drug.objects.create(drug_name="Другой препарат")
    second.drug_groups.add(drug_group)
    TradeName.objects.create(name="Аспирин-Торговый", drug=second)

    response = client.get(
        "/api/v1/search-drugs/",
        {"q": "Аспирин"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data[DATA]["count"] == 2
    assert response.data[DATA]["results"][0]["id"] == first.id
    assert response.data[DATA]["results"][1]["id"] == second.id


@pytest.mark.django_db
def test_search_drugs_without_query_api(client):
    """Поиск без q возвращает 400."""
    response = client.get("/api/v1/search-drugs/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[RESULT]["message"] == 'Параметр "q" обязателен'


@pytest.mark.django_db
def test_search_drugs_with_blank_query_api(client):
    """Пустой q после strip также возвращает 400."""
    response = client.get(
        "/api/v1/search-drugs/",
        {"q": "   "},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[RESULT]["message"] == 'Параметр "q" обязателен'

# ---------------------------------------------------------------------------
# BannedPairLoadView
# ---------------------------------------------------------------------------
@pytest.fixture
def banned_pair_url():
    """URL для загрузки запрещённых пар."""
    return "/api/v1/BannedPair/"

@pytest.fixture
def sample_drugs_for_pairs(db):
    """Создаёт препараты для тестов загрузчика пар."""
    Drug.objects.create(drug_name="амоксициллин")
    Drug.objects.create(drug_name="пробенецид")
    Drug.objects.create(drug_name="варфарин")
    Drug.objects.create(drug_name="ривароксабан")

@pytest.mark.django_db
def test_upload_csv_banned_pairs(client, banned_pair_url, sample_drugs_for_pairs, tmp_path):
    """Успешная загрузка CSV файла с парами."""
    csv_content = "first_drug;second_drug\nамоксициллин;пробенецид\nварфарин;ривароксабан\n"
    file_path = tmp_path / "pairs.csv"
    file_path.write_text(csv_content, encoding="utf-8")

    with open(file_path, 'rb') as f:
        response = client.post(
            banned_pair_url,
            {"file": f},
            format='multipart'
        )

    assert response.status_code == status.HTTP_200_OK
    assert BannedDrugPair.objects.count() == 2
    assert response.data[RESULT]["message"] == "Запрещённые пары ЛС импортированы в БД успешно"

@pytest.mark.django_db
def test_upload_json_banned_pairs(client, banned_pair_url, sample_drugs_for_pairs, tmp_path):
    """Успешная загрузка JSON файла с парами."""
    json_data = [
        {
            "drug": "амоксициллин",
            "banned_drugs": ["пробенецид"]
        },
        {
            "drug": "варфарин",
            "banned_drugs": ["ривароксабан"]
        }
    ]
    json_str = json.dumps(json_data, ensure_ascii=False)
    file_path = tmp_path / "pairs.json"
    file_path.write_text(json_str, encoding="utf-8")

    with open(file_path, 'rb') as f:
        response = client.post(
            banned_pair_url,
            {"file": f},
            format='multipart'
        )

    assert response.status_code == status.HTTP_200_OK
    assert BannedDrugPair.objects.count() == 2
    assert response.data[RESULT]["message"] == "Запрещённые пары ЛС импортированы в БД успешно"

@pytest.mark.django_db
def test_upload_banned_pairs_unsupported_extension(client, banned_pair_url, sample_drugs_for_pairs, tmp_path):
    """Загрузка файла с неподдерживаемым расширением возвращает 400."""
    file_path = tmp_path / "pairs.txt"
    file_path.write_text("амоксициллин;пробенецид", encoding="utf-8")

    with open(file_path, 'rb') as f:
        response = client.post(
            banned_pair_url,
            {"file": f},
            format='multipart'
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[RESULT]["message"] == "Файл должен быть .csv, .xlsx, .xls или .json"

@pytest.mark.django_db
def test_upload_banned_pairs_missing_file(client, banned_pair_url):
    """Запрос без файла возвращает 400."""
    response = client.post(banned_pair_url, {}, format='multipart')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[RESULT]["message"] == "Неверный excel-файл"