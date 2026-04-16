"""Модуль очистки таблицы противопоказаний."""

from abc import ABC, abstractmethod

from django.db import connection

from drugs.models import Drug
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
                f'TRUNCATE TABLE "{self.model._meta.db_table}" '
                'RESTART IDENTITY CASCADE;'
            )


class SQLiteCleaner(ContraindicationCleaner):
    """Очиститель БД SQLite от противопоказаний."""

    def clean(self):
        """Очистка таблиц противопоказаний."""
        # Сначала удаляем связи через through модель
        Drug.contraindications.through.objects.all().delete()
        
        # Потом удаляем сами противопоказания
        self.model.objects.all().delete()
        
        # Сбрасываем автоинкремент (если нужно)
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE sqlite_sequence SET seq = 0 "
                f"WHERE name = '{self.model._meta.db_table}'"
            )


class ContraindicationCleanProcessor:
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
