import os
from unittest.mock import patch, Mock
from django.test import TestCase

from logging_system import config

class ConfigTests(TestCase):
    """Тесты для конфигурации логгера."""

    @patch("logging_system.config.os.makedirs")
    @patch("logging_system.config.RotatingFileHandler")
    @patch("logging_system.config.logging.getLogger")
    def test_get_logger_creates_logger_once(self, mock_get_logger, mock_handler, mock_makedirs):
        """Проверяем, что логгер создается с правильными параметрами, и не дублируется."""
        # Имитируем, что у логгера еще нет хендлеров
        mock_logger = Mock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        config.get_logger()

        mock_get_logger.assert_called_with("calculation_api")
        mock_handler.assert_called_once()
        # Проверяем, что хендлер добавлен
        mock_logger.addHandler.assert_called()
        # Проверяем, что добавлен фильтр
        mock_logger.addFilter.assert_called()

    @patch("logging_system.config.os.makedirs")
    @patch("logging_system.config.RotatingFileHandler")
    @patch("logging_system.config.logging.getLogger")
    def test_get_logger_already_has_handlers(self, mock_get_logger, mock_handler, mock_makedirs):
        """Если у логгера уже есть хендлеры, не добавляем новые."""
        mock_logger = Mock()
        mock_logger.handlers = ["existing_handler"]
        mock_get_logger.return_value = mock_logger

        config.get_logger()

        mock_handler.assert_not_called()
        mock_logger.addHandler.assert_not_called()
        mock_logger.addFilter.assert_not_called()

    @patch("logging_system.config.os.makedirs")
    @patch("logging_system.config.RotatingFileHandler")
    @patch("logging_system.config.logging.getLogger")
    def test_logger_uses_git_version_env(self, mock_get_logger, mock_handler, mock_makedirs):
        """Проверяем, что в логгер передается переменная окружения GIT_COMMIT_VERSION."""
        with patch.dict(os.environ, {"GIT_COMMIT_VERSION": "v1.0"}):
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger

            config.get_logger()

            # Проверяем, что фильтр установлен с git_version
            filter_call = mock_logger.addFilter.call_args[0][0]
            self.assertTrue(hasattr(filter_call, "filter"))
            # Можно проверить, что filter устанавливает record.git_version
            record = Mock()
            filter_call.filter(record)
            self.assertEqual(record.git_version, "v1.0")