# backend/ranker/tests/test_validate_input_data.py
import re
import pytest
from unittest.mock import patch
from rest_framework import status
from ranker.views import CalculationAPI

from drugs.utils.custom_response import CustomResponse
from drugs.models import Drug, SideEffect, DrugSideEffect


class TestValidateWeightsCompleteness:
    """Тесты для метода _validate_weights_completeness"""
    
    @pytest.fixture
    def api_instance(self):
        return CalculationAPI()
    
    @patch('ranker.views.SideEffect')
    @patch('ranker.views.Drug')
    @patch('ranker.views.DrugSideEffect')
    @pytest.mark.django_db
    def test_no_side_effects_returns_error(self, mock_dse, mock_drug, mock_se, api_instance):
        """Тест: если нет побочных эффектов → возвращается CustomResponse с ошибкой"""
        # Arrange
        mock_se.objects.count.return_value = 0
        
        # Act
        result = api_instance._validate_weights_completeness()
        
        # Assert
        assert isinstance(result, CustomResponse)
        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert "не загружены" in result.data['result']['message']
    
    @patch('ranker.views.SideEffect')
    @patch('ranker.views.Drug')
    @patch('ranker.views.DrugSideEffect')
    @pytest.mark.django_db
    def test_mismatch_returns_error(self, mock_dse, mock_drug, mock_se, api_instance):
        """Тест: несоответствие actual != expected → ошибка"""
        # Arrange
        mock_se.objects.count.return_value = 10  # 10 побочных эффектов
        mock_drug.objects.count.return_value = 5  # 5 препаратов
        mock_dse.objects.count.return_value = 40  # должно быть 50
        
        # Act
        result = api_instance._validate_weights_completeness()
        
        # Assert
        assert isinstance(result, CustomResponse)
        assert result.status_code == status.HTTP_400_BAD_REQUEST
        assert "Нарушена целостность данных" in result.data['result']['message']
        assert "50" in result.data['result']['message']
        assert "40" in result.data['result']['message']
    
    @patch('ranker.views.SideEffect')
    @patch('ranker.views.Drug')
    @patch('ranker.views.DrugSideEffect')
    @pytest.mark.django_db
    def test_valid_returns_none(self, mock_dse, mock_drug, mock_se, api_instance):
        """Тест: корректные данные → возвращает None"""
        # Arrange
        mock_se.objects.count.return_value = 10
        mock_drug.objects.count.return_value = 5
        mock_dse.objects.count.return_value = 50
        
        # Act
        result = api_instance._validate_weights_completeness()
        
        # Assert
        assert result is None
    
    @patch('ranker.views.SideEffect')
    @patch('ranker.views.Drug')
    @patch('ranker.views.DrugSideEffect')
    @pytest.mark.django_db
    def test_calls_expected_methods(self, mock_dse, mock_drug, mock_se, api_instance):
        """Тест: проверяет, что методы были вызваны с правильными параметрами"""
        # Arrange
        mock_se.objects.count.return_value = 10
        mock_drug.objects.count.return_value = 5
        mock_dse.objects.count.return_value = 50
        
        # Act
        api_instance._validate_weights_completeness()
        
        # Assert
        mock_se.objects.count.assert_called_once()
        mock_drug.objects.count.assert_called_once()
        mock_dse.objects.count.assert_called_once()


class TestValidateWeightsCompletenessRealDB:
    """Тесты с реальной БД (без моков)"""
    
    @pytest.fixture
    def api_instance(self):
        return CalculationAPI()
    
    @pytest.fixture
    def setup_test_data(self, db):
        """Фикстура для создания тестовых данных в БД"""
        
        # Создаём 2 побочных эффекта
        se1 = SideEffect.objects.create(se_name="Головная боль", weight=0.5)
        se2 = SideEffect.objects.create(se_name="Тошнота", weight=0.3)
        
        # Создаём 2 препарата
        drug1 = Drug.objects.create(drug_name="Аспирин")
        drug2 = Drug.objects.create(drug_name="Парацетамол")
        
        return {
            'se': [se1, se2],
            'drugs': [drug1, drug2]
        }
    
    @pytest.mark.django_db
    def test_valid_with_real_data(self, db, api_instance, setup_test_data):
        """Тест с реальными данными и полной матрицей связей"""
        
        # Создаём полную матрицу: 2 препарата × 2 побочки = 4 записи
        for drug in setup_test_data['drugs']:
            for se in setup_test_data['se']:
                DrugSideEffect.objects.create(
                    drug=drug,
                    side_effect=se,
                    probability=0.1,
                    rang_base=0.5,
                    rang_f1=0.6,
                    rang_f2=0.7,
                    rang_freq=0.8,
                    rang_m1=0.9,
                    rang_m2=1.0
                )
        
        # Act
        result = api_instance._validate_weights_completeness()
        
        # Assert
        assert result is None
    
    @pytest.mark.django_db
    def test_mismatch_with_real_data(self, db, api_instance, setup_test_data):
        """Тест с реальными данными и неполной матрицей связей"""
        
        drug1, drug2 = setup_test_data['drugs']
        se1, se2 = setup_test_data['se']
        
        # Создаём неполную матрицу: только 3 связи вместо 4
        DrugSideEffect.objects.create(drug=drug1, side_effect=se1, probability=0.1)
        DrugSideEffect.objects.create(drug=drug1, side_effect=se2, probability=0.2)
        DrugSideEffect.objects.create(drug=drug2, side_effect=se1, probability=0.1)
        # Пропущена drug2-se2
        
        result = api_instance._validate_weights_completeness()
        
        assert isinstance(result, CustomResponse)
        assert result.status_code == status.HTTP_400_BAD_REQUEST
        
        message = result.data['result']['message']
        # Ожидаем: "ожидается 4 записей весов, найдено 3"
        match = re.search(r'ожидается (\d+) .* найдено (\d+)', message)
        assert match is not None, f"Сообщение не соответствует формату: {message}"
        expected, actual = map(int, match.groups())
        
        assert expected == 4, f"Ожидалось 4, получено {expected}"
        assert actual == 3, f"Ожидалось 3, получено {actual}"