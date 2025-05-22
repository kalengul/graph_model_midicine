"""
Модуль команды для импорда данных в БД.

Выполняется в терминале:
python manage.py import_from_excel
"""

from django.core.management.base import BaseCommand

from drugs.utils.loaders import ExcelLoader


class Command(BaseCommand):
    """Команда для импорта данных в БД из файлов."""

    help = 'Импортирует данные из файлов в базу данных.'

    def handle(self, *args, **kwargs):
        """Импорт данных в БД."""
        try:
            ExcelLoader().load_to_db()
            self.stdout.write(self.style.SUCCESS(
                'Данные успешно импортированы!'
            ))
        except Exception as error:
            self.stderr.write(self.style.ERROR(
                f'Ошибка при импорте данных: {error}'
            ))
