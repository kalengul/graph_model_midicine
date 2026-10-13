"""Тесты TablesView."""
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


pytestmark = pytest.mark.django_db


class TestTablesViewPost:

    def _call(self, factory):
        request = factory.post("/api/v1/generate-tables/")
        from ranker.views import TablesView
        return TablesView.as_view()(request)

    @patch("ranker.views.ExcelTableGenerater")
    def test_success(self, MockGen, factory):
        MockGen.return_value.generate_tables.return_value = MagicMock(
            getvalue=MagicMock(return_value=b"x" * 5000)
        )
        assert self._call(factory).status_code == 200

    @patch("ranker.views.ExcelTableGenerater")
    def test_too_small_file(self, MockGen, factory):
        MockGen.return_value.generate_tables.return_value = MagicMock(
            getvalue=MagicMock(return_value=b"x" * 100)
        )
        assert self._call(factory).status_code == 500

    @patch("ranker.views.ExcelTableGenerater")
    def test_exception(self, MockGen, factory):
        MockGen.return_value.generate_tables.side_effect = RuntimeError("boom")
        assert self._call(factory).status_code == 500


class TestTablesViewGet:

    def _call(self, factory):
        request = factory.get("/api/v1/generate-tables/")
        from ranker.views import TablesView
        return TablesView.as_view()(request)

    def test_no_directory(self, factory):
        with patch("ranker.views.settings") as s:
            s.GENERATED_TABLES = "/nonexistent/path/xyz12345"
            assert self._call(factory).status_code == 404

    def test_empty_directory(self, factory):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("ranker.views.settings") as s:
                s.GENERATED_TABLES = tmp
                assert self._call(factory).status_code == 404

    def test_returns_latest(self, factory):
        with tempfile.TemporaryDirectory() as tmp:
            f_old = Path(tmp) / "old.xlsx"
            f_old.write_bytes(b"old")
            f_new = Path(tmp) / "new.xlsx"
            f_new.write_bytes(b"new")
            os.utime(f_old, (1, 1))
            os.utime(f_new, (2, 2))

            with patch("ranker.views.settings") as s:
                s.GENERATED_TABLES = tmp
                response = self._call(factory)

            # вычитываем и закрываем file handle до удаления tmp
            b"".join(response.streaming_content)
            response.close()

            assert response.status_code == 200
            assert 'new.xlsx' in response['Content-Disposition']