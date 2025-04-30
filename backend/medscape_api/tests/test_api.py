"""Модуль тестирования API."""

import pytest
from rest_framework.test import APIClient
from rest_framework import status

from drugs.models import (Drug,
                          DrugGroup)
from medscape_api.models import (TypeDrugsMedScape,
                                 NameDrugsMedScape,
                                 InteractionMedScape)


DATA = 'data'
DESC = 'description'
COMPAT = 'compatibility_medscape'
DRUGS = 'drugs'
COMPATS = ['compatible',
           'incompatible',
           'caution']
MESSAGE = 'message'
RESULT = 'result'


# @pytest.mark.django_db
# def test_iteraction_medscape_api_plug_204():
#     """Проверка получения совместимости по Medscape со статусом 204."""
#     drug_name_1 = 'амиодарон'
#     drug_name_2 = 'амлодипин'
#     group = DrugGroup.objects.create(dg_name='группа ЛС')
#     Drug.objects.create(drug_name=drug_name_1,
#                         drug_group=group)
#     Drug.objects.create(drug_name=drug_name_2,
#                         drug_group=group)

#     url = '/api/v1/iteraction_medscape/?drugs=[1, 2]'
#     response = APIClient().get(url)

#     assert response.status_code == status.HTTP_204_NO_CONTENT, (
#         'при успешном получении совместимости код статуса должен равняться 204'
#     )
#     print('response.data =', response.data)
#     assert MESSAGE in response.data[RESULT], 'Нет сообщения'
#     assert len(response.data[DATA]) != 0, 'тело ответа пустое'
#     assert COMPAT in response.data[DATA], (
#         'в теле ответа нет информации о совместимости')
#     assert DESC in response.data[DATA], (
#         'в теле ответа нет описания взаимодействия')
#     assert DRUGS in response.data[DATA], 'в теле ответа нет названий ЛС'
#     assert response.data[RESULT][MESSAGE] == 'Совместимость ЛС по MedScape не найдена'
#     assert response.data[DATA][COMPAT] == ('Информация о совместимости'
#                                            ' в MedScape отсутствует'), (
#         'статус совместимости не верный')
#     assert ([drug_name_1, drug_name_2]) == response.data[DATA][DRUGS], (
#         'Выходные ЛС не совпадают с входными') 


# @pytest.mark.django_db
# def test_iteraction_medscape_api_plug_200():
    # """Проверка получения совместимости по Меdscape со статусом 200."""
    # drug_name_1 = 'Амиодарон'
    # drug_name_2 = 'ЛС 2'
    # drug_name_3 = 'ЛС 3'
    # drug_name_4 = 'Ацетазоламид'
    
    # group = DrugGroup.objects.create(dg_name='группа ЛС')
    # Drug.objects.create(drug_name=drug_name_1,
    #                     drug_group=group)
    # Drug.objects.create(drug_name=drug_name_2,
    #                     drug_group=group)
    # Drug.objects.create(drug_name=drug_name_3,
    #                     drug_group=group)
    # Drug.objects.create(drug_name=drug_name_4,
    #                     drug_group=group)

    # url = '/api/v1/iteraction_medscape/?drugs=[1, 4]'
    # response = APIClient().get(url)

    # assert response.status_code == status.HTTP_200_OK, (
    #     'при успешном получении совместимости код статуса должен равняться 200'
    # )
    # assert MESSAGE in response.data[RESULT], 'Нет сообщения'
    # assert len(response.data[DATA]) != 0, 'тело ответа пустое'
    # assert COMPAT in response.data[DATA], (
    #     'в теле ответа нет информации о совместимости')
    # assert DESC in response.data[DATA], (
    #     'в теле ответа нет описания взаимодействия')
    # assert DRUGS in response.data[DATA], 'в теле ответа нет названий ЛС'
    # assert response.data[DATA][COMPAT], 'статус пустой'
    # assert response.data[DATA][COMPAT] in COMPATS, (
    #     'статус совместимости не верный')
    # assert response.data[RESULT][MESSAGE] == (
    #     'Совместимость ЛС по MedScape успешно расcчитана')
    # assert response.data[DATA][DESC], 'описание пустое'
    # assert response.data[DATA][DESC] != 'Справка в MedScape отсутствует', (
    #     'описание пустое')
    # assert ([drug_name_1, drug_name_4]) == response.data[DATA][DRUGS], (
    #     'Выходные ЛС не совпадают с входными')


@pytest.mark.django_db
def test_iteraction_medscape_api_404():
    """Проверка получения совместимости по Меdscape со статусом 404."""
    url = '/api/v1/iteraction_medscape/?drugs=[1, 2]'
    response = APIClient().get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND, (
        'при успешном получении совместимости код статуса должен равняться 404'
    )
    assert len(response.data[DATA]) == 0, 'тело ответа не пустое'
    assert MESSAGE in response.data[RESULT], 'Нет сообщения'
    assert response.data[RESULT][MESSAGE] == 'Ресурс не найден'


@pytest.mark.django_db
def test_iteraction_medscape_api_204():
    """Проверка получения ответа со статусом 204."""
    drug_name_1 = 'ЛС1'
    drug_name_2 = 'ЛС2'
    group = DrugGroup.objects.create(dg_name='группа ЛС')
    Drug.objects.create(drug_name=drug_name_1,
                        drug_group=group)
    Drug.objects.create(drug_name=drug_name_2)

    url = '/api/v1/iteraction_medscape/?drugs=[1, 2]'
    client = APIClient()
    response = client.get(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT, (
        'при успешном получении совместимости код статуса должен равняться 204'
    )
    print('response.data =', response.data)
    assert MESSAGE in response.data[RESULT], 'Нет сообщения'
    assert len(response.data[DATA]) != 0, 'тело ответа пустое'
    assert COMPAT in response.data[DATA], (
        'в теле ответа нет информации о совместимости')
    assert DESC in response.data[DATA], (
        'в теле ответа нет описания взаимодействия')
    assert DRUGS in response.data[DATA], 'в теле ответа нет названий ЛС'
    assert response.data[RESULT][MESSAGE] == 'Совместимость ЛС по MedScape не найдена'
    assert response.data[DATA][COMPAT] == ('Информация о совместимости'
                                           ' в MedScape отсутствует'), (
        'статус совместимости не верный')
    assert ([drug_name_1, drug_name_2]) == response.data[DATA][DRUGS], (
        'Выходные ЛС не совпадают с входными') 

    type = TypeDrugsMedScape.objects.create(type_en='type in english',
                                            type_ru='типа на русском')
    NameDrugsMedScape.objects.create(name_ru='ЛС1',
                                     name_en='MD1',
                                     group_type=type)
    NameDrugsMedScape.objects.create(name_ru='ЛС2',
                                     name_en='MD2',
                                     group_type=type)

    response = client.get(url)

    assert MESSAGE in response.data[RESULT], 'Нет сообщения'
    assert len(response.data[DATA]) != 0, 'тело ответа пустое'
    assert COMPAT in response.data[DATA], (
        'в теле ответа нет информации о совместимости')
    assert DESC in response.data[DATA], (
        'в теле ответа нет описания взаимодействия')
    assert DRUGS in response.data[DATA], 'в теле ответа нет названий ЛС'
    assert response.data[RESULT][MESSAGE] == 'Совместимость ЛС по MedScape не найдена'
    assert response.data[DATA][COMPAT] == ('Информация о совместимости'
                                           ' в MedScape отсутствует'), (
        'статус совместимости не верный')
    assert ([drug_name_1, drug_name_2]) == response.data[DATA][DRUGS], (
        'Выходные ЛС не совпадают с входными') 
