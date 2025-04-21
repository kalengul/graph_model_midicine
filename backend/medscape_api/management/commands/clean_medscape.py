"""Модуль команды очистки таблицы моделей из drugs."""

from abc import ABC, abstractmethod

from django.core.management.base import BaseCommand
from django.db import connection
from medscape_api.models import (DrugGroup,
                                 Drug,
                                 NameDrugsMedScape,
                                 TypeDrugsMedScape,
                                 SourceDrugsMedScape,
                                 WarningsMedScape,
                                 AdverseEffectsMedScape,
                                 PregnancyAndLactationMedScape,
                                 InteractionMedScape,
                                 DrugsInformationMedScape,
                                 DrugInteractionTable,)


class Command(BaseCommand):
    """Команда очистки таблицы."""

    help = ('Очищает таблицы medscape и сбрасывает автоинкремент id')

    class BaseCleaner(ABC):
        """Абстрактный очиститель таблиц."""

        table_names = [
                    'medscape_api_druggroup',
                    'medscape_api_drug',
                    'medscape_api_namedrugsmedscape',
                    'medscape_api_typedrugsmedscape',
                    'medscape_api_sourcedrugsmedscape',
                    'medscape_api_warningsmedscape',
                    'medscape_api_adverseeffectsmedscape',
                    'medscape_api_pregnancyandlactationmedscape',
                    'medscape_api_interactionmedscape',
                    'medscape_api_drugsinformationmedscape',
                    'medscape_api_druginteractiontable',
                ]
<<<<<<< HEAD
        model_classes = [Drug,
                         DrugGroup,
=======
        model_classes = [DrugInteractionTable,
                         DrugsInformationMedScape,
                         InteractionMedScape,
                         PregnancyAndLactationMedScape,
                         AdverseEffectsMedScape,
>>>>>>> 960f7f5bb16db56a09fd3fd2eb5c8142ddc3a287
                         NameDrugsMedScape,
                         TypeDrugsMedScape,
                         SourceDrugsMedScape,
                         WarningsMedScape,
<<<<<<< HEAD
                         AdverseEffectsMedScape,
                         PregnancyAndLactationMedScape,
                         InteractionMedScape,
                         DrugsInformationMedScape,
                         DrugInteractionTable]
=======
                         Drug,
                         DrugGroup,]
>>>>>>> 960f7f5bb16db56a09fd3fd2eb5c8142ddc3a287

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
