"""Модуль команды очистки таблицы моделей из drugs."""

from abc import ABC, abstractmethod

from django.core.management.base import BaseCommand
from django.db import connection
from drugs.models import (DrugGroup,
                          Drug,
                          SideEffect,
                          DrugSideEffect)


class Command(BaseCommand):
    """Команда очистки таблицы."""

    help = ('Очищает таблицы DrugGroup, Drug, SideEffect, '
            'DrugSideEffect и сбрасывает автоинкремент id')

    class BaseCleaner(ABC):
        """Абстрактный очиститель таблиц."""

        table_names = [
                    'drugs_druggroup',
                    'drugs_drug',
                    'drugs_sideeffect',
                    'drugs_drugsideeffect',
                ]
        model_classes = [Drug,
                         DrugGroup,
                         SideEffect,
                         DrugSideEffect,]

        @abstractmethod
        def clear_table(self):
            """Очистка таблиц."""

    class SQLiteCleaner(BaseCleaner):
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

    class PostgresCleaner(BaseCleaner):
        """Очиститель таблиц в БД PostgreSQL."""

        def clear_table(self):
            """Очистака таблиц."""
            with connection.cursor() as cursor:
                cursor.execute((f"TRUNCATE TABLE {', '.join(self.table_names)}"
                                " RESTART IDENTITY CASCADE;"))

    def get_cleaner(self):
        """Определение типа БД."""
        engine = connection.settings_dict['ENGINE']
        if 'sqlite3' in engine:
            return self.SQLiteCleaner()
        elif 'postgresql' in engine:
            return self.PostgresCleaner()
        else:
            raise NotImplementedError(f"Неизвестный движок БД: {engine}")

    def handle(self, *args, **kwargs):
        """Выполнение очистки таблиц."""
        cleaner = self.get_cleaner()
        cleaner.clear_table()
        self.stdout.write(self.style.SUCCESS(
            'Таблицы очищены и id сброшены'))
