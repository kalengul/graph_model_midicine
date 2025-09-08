"""Модуль очистки БД от графов."""

from abc import ABC, abstractmethod

from django.db import connection

from graphs.models import Graph


class GraphCleaner(ABC):
    """Очиститель графов."""
    model = Graph

    @abstractmethod
    def clean(self):
        """Очистка таблицы графов."""


class PostgresCleaner(GraphCleaner):
    """Очиститель БД Postgres от графов."""

    def clean(self):
        """таблицы графов."""
        with connection.cursor() as cursor:
            cursor.execute(
                (f'TRUNCATE TABLE "{self.model._meta.db_table}"' 
                 'RESTART IDENTITY CASCADE;'))

class SQLiteCleaner(GraphCleaner):
    """Очиститель БД SQLite от графов."""

    def clean(self):
        """таблицы графов."""
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
