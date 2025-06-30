"""Модуль очистителя БД синонимов."""

from abc import abstractmethod

from django.db import connection

from drugs.utils.cleaner import BaseCleaner

from synonyms.models import Synonym, SynonymGroup, SynonymStatus


class SynonymCleaner(BaseCleaner):
    """Очиститель синонимов."""

    table_names = [
        'synonyms_synonym',
        'synonyms_synonymgroup',
        'synonyms_synonymstatus'
    ]

    model_classes = [
        Synonym,
        SynonymGroup,
        SynonymStatus
    ]


    @abstractmethod
    def clear_table(self):
        """Очистка таблиц для синонимов."""


class SQLiteCleaner(SynonymCleaner):
    """Очиститель таблиц в SQLite."""

    def clear_table(self):
        """Очистка таблиц."""
        for model in self.model_classes:
            model.objects.all().delete()
        with connection.cursor() as cursor:
            for table in self.table_names:
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name=%s",
                    [table])


class PostgresCleaner(SynonymCleaner):
    """Очиститель таблиц в БД PostgreSQL."""

    def clear_table(self):
        """Очистка таблиц."""
        with connection.cursor() as cursor:
            cursor.execute((f"TRUNCATE TABLE {', '.join(self.table_names)}"
                            " RESTART IDENTITY CASCADE;"))


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

