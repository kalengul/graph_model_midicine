"""
Модуль команды для полной загрузки данных БД.

Выполняется в терминале:
python manage.py full_load_data
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    """Команда для полной загрузки данных БД."""

    help = 'Полная загрузка данных.'

    def handle(self, *args, **options):
        """Полная загрузка данных в БД."""

        try:
            call_command('custom_clear')
            # call_command('clean_medscape')
            call_command('clear_synonyms')
            call_command('migrate')
            call_command('import_data')
            # call_command('load_medscape_data')
            call_command('import_synonyms')
            self.stdout.write('Полина - Великолепная!')
        except Exception as error:
            self.stderr.write(
                self.style.ERROR(
                    f'Ошибка при полной загрузки данных в БД: {error}'
                )
            )

