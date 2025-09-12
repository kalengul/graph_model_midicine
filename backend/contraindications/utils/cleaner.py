"""Модуль очистки таблицы противопоказаний."""

from abc import ABC, abstractmethod

from django.db import connection

from contraindications.models import Contraindication


class ContraindicationCleaner(ABC):
    """Очиститель противопоказаний."""

    model = Contraindication

    @abstractmethod
    def clean(self):
        """Очистка таблицы графов."""


class PostgresCleaner(ContraindicationCleaner):
    """Очиститель БД Postgres от противопоказаний."""

    def clean(self):
        """таблицы противопоказаний."""
        with connection.cursor() as cursor:
            cursor.execute(
                (f'TRUNCATE TABLE "{self.model._meta.db_table}"' 
                 'RESTART IDENTITY CASCADE;'))


class SQLiteCleaner(ContraindicationCleaner):
    """Очиститель БД SQLite от противопоказаний."""

    def clean(self):
        """таблицы противопоказаний."""
        self.model.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute(('DELETE FROM sqlite_sequence'
                            f'WHERE name="{self.model._meta.db_table}"'))


class CleanProcessor:
    """Процессор очистки БД."""

    def get_cleaner(self):
        """Определение типа БД."""
        engine = connection.settings_dict['ENGINE']
        if 'sqlite3' in engine:
            return SQLiteCleaner()
        elif 'postgresql' in engine:
            return PostgresCleaner()
        else:
            raise NotImplementedError(f"Неизвестный движок БД: {engine}")
