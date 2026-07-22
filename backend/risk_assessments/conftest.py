"""
Локальные фикстуры только для risk_assessments
Не зависит от других приложений
"""
import pytest
from rest_framework.test import APIRequestFactory


@pytest.fixture
def factory():
    """Фабрика запросов для тестов"""
    return APIRequestFactory()


@pytest.fixture
def sample_data():
    """Пример данных для тестов"""
    return {
        "compatible_data": {
            "compatibility": "compatible",
            "effects": [{"se_name": "test", "rank": 0.5}]
        },
        "caution_data": {
            "compatibility": "caution",
            "effects": [{"se_name": "warning", "rank": 0.7}]
        }
    }


@pytest.fixture
def sample_drugs():
    """Пример списка лекарств"""
    return ["варфарин", "ампициллин"]


@pytest.fixture
def sample_patient_profile():
    """
    Пример профиля пациента.
    gender строго "man" / "woman" — соответствует enum в PatientProfileSerializer.
    """
    return {
        "gender": "man",
        "age": 45,
        "contList": ["анемия", "гипертония"]
    }