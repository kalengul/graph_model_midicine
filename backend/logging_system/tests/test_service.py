from unittest.mock import patch, Mock
from django.test import TestCase

from logging_system.models import SystemState
from logging_system.services import CalculationLoggingService


class ServicesTests(TestCase):
    """Тесты для CalculationLoggingService."""

    def setUp(self):
        self.state = SystemState.objects.create(id=1, logging_enabled=True)

    @patch("logging_system.services._logger")
    def test_is_enabled_true(self, mock_logger):
        """is_enabled возвращает True, если логирование включено."""
        self.state.logging_enabled = True
        self.state.save()
        self.assertTrue(CalculationLoggingService.is_enabled())

    @patch("logging_system.services._logger")
    def test_is_enabled_false(self, mock_logger):
        """is_enabled возвращает False, если логирование выключено."""
        self.state.logging_enabled = False
        self.state.save()
        self.assertFalse(CalculationLoggingService.is_enabled())

    @patch("logging_system.services._logger")
    def test_set_enabled_turns_on(self, mock_logger):
        """Включение логирования."""
        self.state.logging_enabled = False
        self.state.save()
        CalculationLoggingService.set_enabled(True)
        self.state.refresh_from_db()
        self.assertTrue(self.state.logging_enabled)
        mock_logger.info.assert_called_with("Логирование включено")

    @patch("logging_system.services._logger")
    def test_set_enabled_turns_off(self, mock_logger):
        """Выключение логирования."""
        self.state.logging_enabled = True
        self.state.save()
        CalculationLoggingService.set_enabled(False)
        self.state.refresh_from_db()
        self.assertFalse(self.state.logging_enabled)
        mock_logger.info.assert_called_with("Логирование выключено")

    @patch("logging_system.services._logger")
    def test_set_enabled_no_change(self, mock_logger):
        """Если состояние не меняется, лог не пишется."""
        self.state.logging_enabled = True
        self.state.save()
        CalculationLoggingService.set_enabled(True)
        mock_logger.info.assert_not_called()

    @patch("logging_system.services._logger")
    def test_log_request_when_enabled(self, mock_logger):
        """Логирование при включённом логировании."""
        self.state.logging_enabled = True
        self.state.save()

        user = Mock(username="testuser", is_authenticated=True)

        CalculationLoggingService.log_request(
            user,
            status="caution",
            rank=0.53,
            drug_ids=[1, 2],
            missing_drugs=[],
            all_drugs=["drugA", "drugB"],
        )

        mock_logger.info.assert_called_once()
        line = mock_logger.info.call_args[0][0]

        assert "User: testuser" in line
        assert "Status: caution" in line
        assert "Rank: 0.53" in line
        assert "DrugIds: [1, 2]" in line
        assert "Drugs: ['drugA', 'drugB']" in line

    @patch("logging_system.services.Drug")
    @patch("logging_system.services._logger")
    def test_log_request_anonymous_user(self, mock_logger, mock_drug):
        """Пользователь Anonymous."""
        self.state.logging_enabled = True
        self.state.save()

        user = Mock(is_authenticated=False)
        mock_drug.objects.filter.return_value.values_list.return_value = []

        CalculationLoggingService.log_request(user, [])
        log_call = mock_logger.info.call_args[0][0]
        self.assertIn("User: Anonymous", log_call)

    @patch("logging_system.services.SystemState.get_current_state")
    def test_is_enabled_fallback_when_db_error(self, mock_get_state):
        """При ошибке БД is_enabled() возвращает True (fallback)."""
        mock_get_state.side_effect = Exception("DB connection error")
        self.assertTrue(CalculationLoggingService.is_enabled())