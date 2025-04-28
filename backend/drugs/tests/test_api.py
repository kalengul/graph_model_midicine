"""Модуль тестов API."""

import pytest
from rest_framework.test import APIClient
from rest_framework import status

from drugs.models import (Drug,
                          DrugGroup,
                          SideEffect,
                          DrugSideEffect)


FORMAT = 'json'
DATA = 'data'


@pytest.mark.django_db
def test_add_drug_group_api():
    """Проверка добавления группы ЛС."""
    client = APIClient()
    url = '/api/v1/addDrugGroup/'
    adding_drug_group = {
        "dg_name": "диуретики"
    }

    response = client.post(url, adding_drug_group, format=FORMAT)

    assert response.status_code == status.HTTP_200_OK, 'добавление не успешно'
    assert DrugGroup.objects.count() == 1, 'В БД не появилась новой группы ЛС'
    assert response.data[DATA]['dg_name'] == adding_drug_group['dg_name'], (
        'в ответе не правильное название группы ЛС')


@pytest.mark.django_db
def test_get_drug_group_list_api():
    """Проверка получения списка групп ЛС."""
    DrugGroup.objects.create(dg_name='Группа ЛС.')
    DrugGroup.objects.create(dg_name='Группа ЛС 2.')

    client = APIClient()
    url = '/api/v1/getDrugGroup/'

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK, (
        'список группы ЛС не удалось получить')
    assert len(response.data[DATA]) != 0, 'пустое тело ответа'
    assert len(response.data[DATA][0]) == 2, (
        'в ответе не праивильное число параметров')
    assert 'dg_name' in response.data[DATA][0], (
        'в ответе нет названия группы ЛС')
    assert 'id' in response.data[DATA][0], 'в ответе нет ID группы ЛС'


@pytest.mark.django_db
def test_get_drug_group_detail_api():
    """Проверка получения отдельного ЛС."""
    DrugGroup.objects.create(dg_name='Группа ЛС.')
    DrugGroup.objects.create(dg_name='Группа ЛС 2.')

    client = APIClient()
    url = '/api/v1/getDrugGroup/?dg_id=1'

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK, (
        'при успешном получении группы ЛС код должен быть 200')
    assert len(response.data[DATA]) != 0, 'пустое тело ответа'
    assert 'dg_name' in response.data[DATA], (
        'в ответе нет названия группы ЛС')
    assert 'id' in response.data[DATA], 'в ответе нет ID группы ЛС'


@pytest.mark.django_db
def test_delete_drug_group_api():
    """Проверка удаления."""
    DrugGroup.objects.create(dg_name='Группа ЛС.')

    client = APIClient()
    url = '/api/v1/deleteDrugGroup/?dg_id=1'

    response = client.delete(url)
    assert response.status_code == status.HTTP_200_OK, (
        'при успешном удаление группы ЛС код должен быть 200'
    )
    assert DrugGroup.objects.count() == 0, 'группа ЛС не удалена'


@pytest.mark.django_db
def test_add_drug_api():
    """Проверка добавления ЛС."""
    DrugGroup.objects.create(dg_name = 'группа ЛС')
    SideEffect.objects.create(se_name='ПД')

    adding_drug = {
        "drug_name": "ЛС",
        "side_effects": [
            {
                "se_id": 1,
                "rank": 0.8
            }
        ]
    }

    url = '/api/v1/addDrug/'
    client = APIClient()
    response = client.post(url, adding_drug, format=FORMAT)
    print('response.status_code =', response.status_code)
    assert response.status_code == status.HTTP_200_OK, (
        'при успешном добавлении ЛС код статуса должен равняться 200'
    )
    assert Drug.objects.count() == 1, 'ЛС не добавлено'
    assert len(response.data[DATA]) != 0, 'тело ответа пустое'
    assert 'id' in response.data[DATA], 'в теле ответа нет id ЛС'
    assert 'drug_name' in response.data[DATA], 'в теле ответа нет "drug_name"'


@pytest.mark.django_db
def test_get_drug_list_api():
    """Проверка получения списка."""
    drug_group = DrugGroup.objects.create(dg_name='Группа ЛС.')
    Drug.objects.create(drug_name='ЛС1',
                        drug_group=drug_group)

    client = APIClient()
    url = '/api/v1/getDrug/'

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK, (
        'при получении списка ЛС код статуса должен быть 200')
    assert len(response.data[DATA]) != 0, 'тело ответа - пустое'
    assert len(response.data[DATA][0]) == 2, (
        'в теле ответа некорректные параметры')
    assert 'drug_name' in response.data[DATA][0], (
        'в теле ответа нет поля "drug_name"')
    assert 'id' in response.data[DATA][0], 'в теле ответа нет поля "id"'


@pytest.mark.django_db
def test_get_drug_detail_api():
    """Проверка получения одного ЛС."""
    drug_group = DrugGroup.objects.create(dg_name='Группа ЛС.')
    Drug.objects.create(drug_name='ЛС1',
                        drug_group=drug_group)

    client = APIClient()
    url = '/api/v1/getDrug/?drug_id=1'
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK, (
        'при получении ЛС код статуса должен быть 200')
    assert len(response.data[DATA]) != 0, 'тело ответа - пустое'
    assert 'drug_name' in response.data[DATA], (
        'в теле ответа нет поля "drug_name"')
    assert 'id' in response.data[DATA], 'в теле ответа нет поля "id"'


@pytest.mark.django_db
def test_delete_drug_api():
    """Проверка удаления ЛС."""
    drug_group = DrugGroup.objects.create(dg_name='Группа ЛС.')
    Drug.objects.create(drug_name='ЛС1',
                        drug_group=drug_group)

    client = APIClient()
    url = '/api/v1/deleteDrug/?drug_id=1'
    response = client.delete(url)
    assert response.status_code == status.HTTP_200_OK, (
        'при успешном удалении код статуса должен равняться 200')
    assert Drug.objects.count() == 0, 'ЛС не удалено'
    assert len(response.data[DATA]) == 0, 'Тело ответа должно быть пустыми'


@pytest.mark.django_db
def test_add_side_effect_api():
    """Проверка добавления ПД."""
    Drug.objects.create(
        drug_name='ЛС',
        drug_group=DrugGroup.objects.create(dg_name='группа ЛС'))
    client = APIClient()
    url = '/api/v1/addSideEffect/'
    adding_side_effect = {
        "se_name": "почечная недостаточность",
        "side_effects": [
            {
                "drug_id": 1,
                "rank": 0.8,
            }
        ],
    }
    response = client.post(url, adding_side_effect, format=FORMAT)
    assert response.status_code == status.HTTP_200_OK, (
        'при успешном добавлении ПД код статуса должен равнять 200')
    assert SideEffect.objects.count() == 1, 'ПД не был доваблен'
    assert len(response.data[DATA]) != 0, 'Тело пустое'
    assert 'id' in response.data[DATA], 'В теле ответа нет id ПД'
    assert 'se_name' in response.data[DATA], 'В теле ответа нет название ПД'


@pytest.mark.django_db
def test_get_side_effect_list_api():
    """Проверка получение списка ПД."""
    SideEffect.objects.create(se_name='ПД1')
    SideEffect.objects.create(se_name='ПД2')
    client = APIClient()
    url = '/api/v1/getSideEffect/'
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK, (
        'при успешном получении списка ПД код статуса должен быть 200')
    assert len(response.data[DATA]) != 0, 'тело ответа пустое'
    assert len(response.data[DATA][0]) != 0, 'список не содержит данных о ПД'
    assert 'id' in response.data[DATA][0], 'в теле ответа нет id ПД'
    assert 'se_name' in response.data[DATA][0], (
        'в теле ответа нет названия ПД')


@pytest.mark.django_db
def test_get_side_effect_detail_api():
    """Проверка получение отдельного ПД."""
    SideEffect.objects.create(se_name='ПД1')
    client = APIClient()
    url = '/api/v1/getSideEffect/?se_id=1'
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK, (
        'при успешном получении ПД код статуса должен быть 200')
    assert len(response.data[DATA]) != 0, 'тело ответа пустое'
    assert 'id' in response.data[DATA], 'в теле ответа нет id ПД'
    assert 'se_name' in response.data[DATA], 'в теле ответа нет названия ПД'


@pytest.mark.django_db
def test_delete_side_effect_api():
    """Проверка удаления ПД."""
    SideEffect.objects.create(se_name='ПД1')
    client = APIClient()
    url = '/api/v1/deleteSideEffect/?se_id=1'
    response = client.delete(url)
    assert response.status_code == status.HTTP_200_OK, (
        'при успешном удалении ПД код статуса должен быть 200')
    assert SideEffect.objects.count() == 0, 'ПД не удалён'
    assert len(response.data[DATA]) == 0, 'тело ответа не пустое'


@pytest.mark.django_db
def test_get_ranks_api():
    """Проверка получение рангов."""
    DrugSideEffect.objects.create(
        drug=Drug.objects.create(
            drug_group=DrugGroup.objects.create(dg_name='ГЛС'),
            drug_name='ЛС'),
        side_effect=SideEffect.objects.create(se_name='ПД'))
    url = '/api/v1/getRanks/'
    client = APIClient()
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK, (
        'при успешном получении рангов код статусоса должен равнятся 200')
    assert len(response.data[DATA]) != 0, 'тело ответа пустое'
    assert len(response.data[DATA][0]) == 3, 'формам тела ответа неверный'
    assert 'se_id' in response.data[DATA][0], 'в ответе нет id ПД'
    assert 'drug_id' in response.data[DATA][0], 'в ответе нет id ЛС'
    assert 'rank' in response.data[DATA][0], 'в ответе нет id ПД'


@pytest.mark.django_db
def test_change_ranks_api():
    """Проверка изменения рангов."""
    ranks = DrugSideEffect.objects.create(
                drug=Drug.objects.create(
                    drug_group=DrugGroup.objects.create(dg_name='ГЛС'),
                    drug_name='ЛС'),
                side_effect=SideEffect.objects.create(se_name='ПД'))
    rank = 0.8
    response = APIClient().put(path='/api/v1/updateRanks/',
                               data={
                                    "update_rsgs": [
                                        {
                                            "drug_id": 1,
                                            "se_id": 1,
                                            "rank": rank,
                                        }
                                    ]
                                },
                               format=FORMAT)

    assert response.status_code == status.HTTP_200_OK, (
        'при успешно изменении ранга кода статуса должен равняться 200')
    assert len(response.data[DATA]) == 0, 'тело ответа должно быть пустым'
    ranks.refresh_from_db()
    assert ranks.probability == rank, 'ранг не изменился'
