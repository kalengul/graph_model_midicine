"""
Модуль команды для экспорта синонимов из БД.

Выполняется в терминале:
python manage.py export_synonyms.py
"""

import traceback

from django.core.management.base import BaseCommand

from synonyms.utils.json_synonums_loader import InnerJSONSynonymLoader


class Command(BaseCommand):
    """Команда для экспорта синонимов из БД."""

    help = 'Экспорт синонимов из БД в файл.'

    def handle(self, *args, **options):
        """Экспорт синонимов в БД."""
        try:
            InnerJSONSynonymLoader().export_synonyms_to_file()
            self.stdout.write(self.style.SUCCESS(
                    'Синонимы из БД в файл успешно экспортированы!'
                ))
        except Exception as error:
            traceback.print_exc()
            self.stderr.write(self.style.ERROR(
                'Ошибка при экспорте синонимов.'
            ))
