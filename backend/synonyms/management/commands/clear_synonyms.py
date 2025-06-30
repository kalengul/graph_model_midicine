"""
Модуль команды для экспорта экспорта из БД.

Выполняется в терминале:
python manage.py clear_synonyms.py
"""

import traceback

from django.core.management.base import BaseCommand

from synonyms.utils.synonym_cleaner import CleanProcessor


class Command(BaseCommand):
    """Команда для очистки синонимов в БД."""

    help = 'Очистка синонимов.'

    def handle(self, *args, **options):
        """Очистка синонимов."""
        try:
            CleanProcessor().get_cleaner().clear_table()
            self.stdout.write(self.style.SUCCESS(
                'Синонимы очищены успешно.'
            ))
        except Exception as error:
            traceback.print_exc()
            self.stderr.write(self.style.ERROR(
                'Ошибка очистки синонимов.'
            ))
