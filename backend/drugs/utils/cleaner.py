"""Модуль чистильщиков БД."""

from abc import ABC, abstractmethod

from django.db import connection

from drugs.models import (DrugGroup,
                          Drug,
                          SideEffect,
                          DrugSideEffect,
                          BannedDrugPair,
                          Nosology,
                          DrugsAgeContraindications
                          )


class BaseCleaner(ABC):
    """Абстрактный очиститель таблиц."""

    table_names = [
        'drugs_drugsideeffect',
        'drugs_drug',
        'drugs_sideeffect',
        'drugs_druggroup',
        'drugs_nosology',
        'drugs_drugsagecontraindications'
    ]
    model_classes = [
        DrugSideEffect,
        Drug,
        SideEffect,
        DrugGroup,
        Nosology,
        DrugsAgeContraindications
    ]

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
                    "DELETE FROM sqlite_sequence WHERE name = %s",
                    [table]
                )


class PostgresCleaner(BaseCleaner):
    """Очиститель таблиц в БД PostgreSQL."""

    def clear_table(self):
        """Очистка таблиц."""
        with connection.cursor() as cursor:
            quoted_tables = [f'"{table}"' for table in self.table_names]
            cursor.execute(
                f"TRUNCATE TABLE {', '.join(quoted_tables)} RESTART IDENTITY CASCADE;"
            )


class DrugCleanProcessor:
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


class BannedDrugPairCleaner(BaseCleaner):
    """Базовый очиститель таблицы БД для пар ЛС."""

    table_names = ['drugs_banneddrugpair',]
    model_classes = [BannedDrugPair,]

    @abstractmethod
    def clear_table(self):
        """Очистка таблиц."""


class SQLiteBannedDrugCleaner(BannedDrugPairCleaner):
    """Очиститель таблицы пар ЛС для SQLite."""

    def clear_table(self):
        """Очистка таблиц."""
        for model in self.model_classes:
            model.objects.all().delete()
        with connection.cursor() as cursor:
            for table in self.table_names:
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name=%s",
                    [table])
    

class PostgresBannedDrugCleaner(BannedDrugPairCleaner):
    """Очиститель таблицы пар ЛС для Postgres."""

    def clear_table(self):
        """Очистка таблиц."""
        with connection.cursor() as cursor:
            quoted_tables = [f'"{table}"' for table in self.table_names]
            cursor.execute(
                f"TRUNCATE TABLE {', '.join(quoted_tables)} "
                "RESTART IDENTITY CASCADE;"
            )


class BannedDrugPairCleanProcessor:
    """Процессор очистки БД."""

    def get_cleaner(self):
        """Определение типа БД."""
        engine = connection.settings_dict['ENGINE']
        if 'sqlite3' in engine:
            return SQLiteBannedDrugCleaner()
        elif 'postgresql' in engine:
            return PostgresBannedDrugCleaner()
        else:
            raise NotImplementedError(f"Неизвестный движок БД: {engine}")
