import os
from unittest.mock import patch, Mock
from django.test import TestCase

from logging_system import config


class ConfigTests(TestCase):
    """Тесты для конфигурации логгера."""

    @patch("logging_system.config.RotatingFileHandler")
    @patch("logging_system.config.logging.getLogger")
    def test_get_logger_creates_logger_once(self, mock_get_logger, mock_handler):
        """Логгер создаётся с правильными параметрами, если у него нет хендлеров."""
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        config.get_logger('fortran_calc', 'fortran_calc.log')

        mock_get_logger.assert_called_with('fortran_calc')
        mock_handler.assert_called_once()
        mock_logger.addHandler.assert_called()
        mock_logger.addFilter.assert_called()

    @patch("logging_system.config.RotatingFileHandler")
    @patch("logging_system.config.logging.getLogger")
    def test_get_logger_already_has_handlers(self, mock_get_logger, mock_handler):
        """Если у логгера уже есть хендлеры — новые не добавляем."""
        mock_logger = Mock()
        mock_logger.handlers = ["existing_handler"]
        mock_get_logger.return_value = mock_logger

        config.get_logger('fortran_calc', 'fortran_calc.log')

        mock_handler.assert_not_called()
        mock_logger.addHandler.assert_not_called()
        mock_logger.addFilter.assert_not_called()

    @patch("logging_system.config.RotatingFileHandler")
    @patch("logging_system.config.logging.getLogger")
    def test_logger_uses_git_version_env(self, mock_get_logger, mock_handler):
        """В логгер передаётся GIT_COMMIT_VERSION из окружения."""
        with patch.dict(os.environ, {"GIT_COMMIT_VERSION": "v1.0"}):
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger

            config.get_logger('fortran_calc', 'fortran_calc.log')

            filter_call = mock_logger.addFilter.call_args[0][0]
            self.assertTrue(hasattr(filter_call, "filter"))
            record = Mock()
            filter_call.filter(record)
            self.assertEqual(record.git_version, "v1.0")

    @patch("logging_system.config.RotatingFileHandler")
    @patch("logging_system.config.logging.getLogger")
    def test_two_loggers_are_independent(self, mock_get_logger, mock_handler):
        """Fortran и risk — разные логгеры с разными именами."""
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        config.get_logger('fortran_calc', 'fortran_calc.log')
        config.get_logger('risk_assessments', 'risk_assesments.log')

        called_names = [c.args[0] for c in mock_get_logger.call_args_list]
        self.assertIn('fortran_calc', called_names)
        self.assertIn('risk_assessments', called_names)