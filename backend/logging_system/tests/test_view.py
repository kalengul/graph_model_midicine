import os
import tempfile
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status

from logging_system.models import SystemState


class ViewsTests(TestCase):
    """Тесты для представлений logging_system."""

    API_BASE = "/api/v1/"

    def setUp(self):
        self.client = APIClient()
        self.state = SystemState.objects.create(id=1)

        # Создаём пользователя и токен
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.auth_header = f'Bearer {self.token.key}'

    def _auth_get(self, url, **kwargs):
        return self.client.get(url, HTTP_AUTHORIZATION=self.auth_header, **kwargs)

    def _auth_post(self, url, data=None, **kwargs):
        return self.client.post(url, data, HTTP_AUTHORIZATION=self.auth_header, **kwargs)

    def _auth_delete(self, url, **kwargs):
        return self.client.delete(url, HTTP_AUTHORIZATION=self.auth_header, **kwargs)

    def test_system_state_get(self):
        url = f"{self.API_BASE}logs/state/"
        response = self._auth_get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["logging_enabled"], self.state.logging_enabled)
        self.assertEqual(data["drugs_file_name"], self.state.drugs_file_name)

    @patch("logging_system.views.SystemState.get_current_state")
    def test_system_state_get_calls_get_current_state(self, mock_get_state):
        mock_get_state.return_value = self.state
        url = f"{self.API_BASE}logs/state/"
        self._auth_get(url)
        mock_get_state.assert_called_once()

    def test_logging_toggle_get(self):
        url = f"{self.API_BASE}logs/toggle/"
        response = self._auth_get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["enabled"], self.state.logging_enabled)

    @patch("logging_system.views.CalculationLoggingService.set_enabled")
    @patch("logging_system.views.CalculationLoggingService.is_enabled")
    def test_logging_toggle_post(self, mock_is_enabled, mock_set_enabled):
        mock_is_enabled.return_value = True
        url = f"{self.API_BASE}logs/toggle/"
        response = self._auth_post(url, {"enabled": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_set_enabled.assert_called_with(False)
        self.assertEqual(response.data["enabled"], True)

        # Проверка ошибки при отсутствии поля
        response = self._auth_post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_logs_export_get_file_exists(self):
        # Создаём временный файл с содержимым
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test log content")
            tmp_path = tmp.name

        # Подменяем путь к лог-файлу на временный
        with patch("logging_system.views.LOG_FILE_PATH", tmp_path):
            # Убеждаемся, что файл существует
            url = f"{self.API_BASE}logs/export/"
            response = self._auth_get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response['Content-Type'], 'text/plain')
            self.assertEqual(response['Content-Disposition'], 'attachment; filename="requested_drugs.log"')
            # Проверяем содержимое
            content = b''.join(response.streaming_content)
            self.assertEqual(content, b"test log content")

        os.unlink(tmp_path)

    def test_logs_export_get_file_not_found(self):
        # Патчим exists, чтобы он возвращал False для любого пути
        with patch("logging_system.views.os.path.exists", return_value=False):
            url = f"{self.API_BASE}logs/export/"
            response = self._auth_get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn("error", response.data)

    def test_logs_delete_delete_success(self):
        # Создаём временный файл с содержимым
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"some logs")
            tmp_path = tmp.name

        with patch("logging_system.views.LOG_FILE_PATH", tmp_path):
            url = f"{self.API_BASE}logs/delete/"
            response = self._auth_delete(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["message"], "Логи очищены")
            # Проверяем, что файл теперь пуст
            with open(tmp_path, 'r') as f:
                self.assertEqual(f.read(), "")

        os.unlink(tmp_path)

    def test_logs_delete_delete_not_found(self):
        with patch("logging_system.views.os.path.exists", return_value=False):
            url = f"{self.API_BASE}logs/delete/"
            response = self._auth_delete(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn("error", response.data)

    def test_logs_delete_delete_internal_error(self):
        # Создаём временный файл, но при открытии на запись выбрасываем исключение
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        with patch("logging_system.views.LOG_FILE_PATH", tmp_path):
            with patch("logging_system.views.os.path.exists", return_value=True):
                with patch("builtins.open", side_effect=Exception("Some error")):
                    url = f"{self.API_BASE}logs/delete/"
                    response = self._auth_delete(url)
                    self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
                    self.assertIn("error", response.data)

        os.unlink(tmp_path)