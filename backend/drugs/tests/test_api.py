"""Модуль тестов API."""

import pytest
from rest_framework.test import APIClient
from django.urls import reverse


@pytest.mark.django_db
def test_get_drug_api():
    client = APIClient()
    url = reverse('get_drug')
    response = client.get(url)
    assert response.status_code == 200
