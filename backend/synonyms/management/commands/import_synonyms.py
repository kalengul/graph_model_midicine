"""
Модуль команды для импорта синонимов в БД.

Выполняется в терминале:
python manage.py import_synonyms.py
"""

import traceback

from django.core.management.base import BaseCommand

from synonyms.utils.json_synonums_loader import InnerJSONSynonymLoader


class Command(BaseCommand):
    """Команда для импорта синонимов в БД."""

    help = 'Импорт синонимов.'

    def handle(self, *args, **options):
        """Импорт синонимов в БД из файла."""
        try:
            InnerJSONSynonymLoader().import_synonyms()
            self.stdout.write(self.style.SUCCESS(
                'Синонимы в БД импортированы успешно!'
            ))
        except Exception as error:
            traceback.print_exc()
            self.stderr.write(self.style.ERROR(
                'Ошибка при импорте синонимов.'
            ))