import hashlib
import tempfile
from unittest.mock import patch, Mock

from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile

from logging_system.utils.calc_hash import calculate_file_hash
from logging_system.utils.get_current_commit_hash import get_current_commit_hash
from logging_system.models import SystemState

class UtilsTests(TestCase):
    """Тесты для утилит."""

    def test_calculate_file_hash_with_uploaded_file(self):
        """Вычисление хеша для UploadedFile."""
        content = b"test content"
        uploaded = UploadedFile(tempfile.NamedTemporaryFile(), content_type="text/plain")
        uploaded.write(content)
        uploaded.seek(0)

        expected_hash = hashlib.md5(content).hexdigest()
        self.assertEqual(calculate_file_hash(uploaded), expected_hash)
        # Проверяем, что указатель вернулся в начало
        self.assertEqual(uploaded.tell(), 0)

    def test_calculate_file_hash_with_regular_file(self):
        """Вычисление хеша для обычного файлового объекта."""
        with tempfile.NamedTemporaryFile() as f:
            f.write(b"test content")
            f.flush()
            f.seek(0)
            expected_hash = hashlib.md5(b"test content").hexdigest()
            self.assertEqual(calculate_file_hash(f), expected_hash)
            self.assertEqual(f.tell(), 0)

    @patch("subprocess.run")
    def test_get_current_commit_hash_success(self, mock_run):
        """Успешное получение хеша коммита."""
        mock_run.return_value = Mock(stdout="abc123\n")
        self.assertEqual(get_current_commit_hash(), "abc123")
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        self.assertIn("git", args[0])
        self.assertIn("rev-parse", args[0])

    @patch("subprocess.run", side_effect=Exception("git error"))
    def test_get_current_commit_hash_failure(self, mock_run):
        """Ошибка при получении хеша."""
        self.assertIsNone(get_current_commit_hash())


class ModelsTests(TestCase):
    """Тесты для модели SystemState."""

    def setUp(self):
        self.state = SystemState.objects.create(id=1)

    @patch("logging_system.models.get_current_commit_hash")
    def test_get_current_state_creates_if_not_exists(self, mock_get_hash):
        """get_current_state создает запись, если её нет."""
        # Удаляем существующую
        SystemState.objects.all().delete()
        mock_get_hash.return_value = "commit123"
        state = SystemState.get_current_state()
        self.assertIsNotNone(state)
        self.assertEqual(state.commit_hash, "commit123")
        # Проверяем, что запись создана
        self.assertEqual(SystemState.objects.count(), 1)

    @patch("logging_system.models.get_current_commit_hash")
    def test_get_current_state_updates_commit_hash(self, mock_get_hash):
        """get_current_state обновляет хэш коммита, если он изменился."""
        state = SystemState.objects.get(id=1)
        state.commit_hash = "oldhash"
        state.save()

        mock_get_hash.return_value = "newhash"
        updated_state = SystemState.get_current_state()
        self.assertEqual(updated_state.commit_hash, "newhash")

        # Проверяем, что сохранилось
        state.refresh_from_db()
        self.assertEqual(state.commit_hash, "newhash")

    @patch("logging_system.models.get_current_commit_hash")
    def test_get_current_state_does_not_update_if_same(self, mock_get_hash):
        """Хэш не обновляется, если он не изменился."""
        state = SystemState.objects.get(id=1)
        state.commit_hash = "samehash"
        state.save()

        mock_get_hash.return_value = "samehash"
        with patch.object(state, "save", wraps=state.save) as mock_save:
            SystemState.get_current_state()
            mock_save.assert_not_called()

    def test_str_method(self):
        """Проверка строкового представления."""
        state = SystemState.objects.get(id=1)
        self.assertIn(str(state.updated_at), str(state))