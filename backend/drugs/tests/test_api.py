"""Модуль тестов API."""

import pytest
from rest_framework.test import APIClient
from rest_framework import status

from drugs.models import (Drug,
                          DrugGroup,
                          SideEffect,
                          DrugSideEffect)


@pytest.mark.django_db
def test_add_drug_group_api():
    """Проверка добавления группы ЛС."""
    client = APIClient()
    url = '/api/v1/addDrugGroup/'
    adding_drug_group = {
        "dg_name": "диуретики"
    }

    response = client.post(url, adding_drug_group, format='json')

    assert response.status_code == status.HTTP_200_OK, 'добавление не успешно'
    assert DrugGroup.objects.count() == 1, 'В БД не появилась новой группы ЛС'
    assert response.data['data']['dg_name'] == adding_drug_group['dg_name'], (
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
    assert len(response.data['data']) != 0, 'пустое тело ответа'
    assert len(response.data['data'][0]) == 2, (
        'в ответе не праивильное число параметров')
    assert 'dg_name' in response.data['data'][0], (
        'в ответе нет названия группы ЛС')
    assert 'id' in response.data['data'][0], 'в ответе нет ID группы ЛС'


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
    assert len(response.data['data']) != 0, 'пустое тело ответа'
    assert 'dg_name' in response.data['data'], (
        'в ответе нет названия группы ЛС')
    assert 'id' in response.data['data'], 'в ответе нет ID группы ЛС'


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
    response = client.post(url, adding_drug, format='json')
    print('response.status_code =', response.status_code)
    assert response.status_code == status.HTTP_200_OK, (
        'при успешном добавлении ЛС код статуса должен равняться 200'
    )
    assert Drug.objects.count() == 1, 'ЛС не добавлено'
    assert len(response.data['data']) != 0, 'тело ответа пустое'
    assert 'id' in response.data['data'], 'в теле ответа нет id ЛС'
    assert 'drug_name' in response.data['data'], 'в теле ответа нет "drug_name"'


@pytest.mark.django_db
def test_get_drug_list_api():
    """Проверка получения списка."""
    drug_group = DrugGroup.objects.create(dg_name='Группа ЛС.')
    Drug.objects.create(drug_name='ЛС1',
                        drug_group=drug_group)

    client = APIClient()
    url = '/api/v1/getDrug/'

    response = client.get(url)
    assert response.status_code == 200, (
        'при получении списка ЛС код статуса должен быть 200')
    assert len(response.data['data']) != 0, 'тело ответа - пустое'
    assert len(response.data['data'][0]) == 2, (
        'в теле ответа некорректные параметры')
    assert 'drug_name' in response.data['data'][0], (
        'в теле ответа нет поля "drug_name"')
    assert 'id' in response.data['data'][0], 'в теле ответа нет поля "id"'


@pytest.mark.django_db
def test_get_drug_detail_api():
    """Проверка получения одного ЛС."""
    drug_group = DrugGroup.objects.create(dg_name='Группа ЛС.')
    Drug.objects.create(drug_name='ЛС1',
                        drug_group=drug_group)

    client = APIClient()
    url = '/api/v1/getDrug/?drug_id=1'
    response = client.get(url)
    assert response.status_code == 200, (
        'при получении ЛС код статуса должен быть 200')
    assert len(response.data['data']) != 0, 'тело ответа - пустое'
    assert 'drug_name' in response.data['data'], (
        'в теле ответа нет поля "drug_name"')
    assert 'id' in response.data['data'], 'в теле ответа нет поля "id"'
