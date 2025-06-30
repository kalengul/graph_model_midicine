"""
Модуль команды для импорта данных в БД.

Выполняется в терминале:
python manage.py import_data
"""

from django.core.management.base import BaseCommand

from drugs.utils.db_manipulator import DBManipulator
from drugs.utils.loaders import ExcelLoader


class Command(BaseCommand):
    """Команда для импорта данных в БД из файлов."""

    help = 'Импортирует данные из файлов в базу данных.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--txt',
            action='store_true',
            help= 'Указывает, что БД заполняется данными из текстовых файлов'
        )

        parser.add_argument(
            '--excel',
            type=str,
            default=None,
            help='Указывает excel-файл для загрузки данных в БД'
        )

    def handle(self, *args, **options):
        """Импорт данных в БД."""
        try:
            txt = options.get('txt')
            excel_path = options.get('excel')
            if txt:
                DBManipulator().load_to_db()
                self.stdout.write(self.style.SUCCESS(
                    'Данные из текстовых файлов успешно импортированы!'
                ))
            elif excel_path:
                ExcelLoader(excel_path).load_to_db()
                self.stdout.write(self.style.SUCCESS(
                    f'Данные из {excel_path} успешно импортированы!'
                ))
            elif not excel_path and not txt:
                ExcelLoader().load_to_db()
                self.stdout.write(self.style.SUCCESS(
                    ('Файл для загрузки не указан. Данные загружены'
                     f' из {ExcelLoader.EXCEL_PATH} успешно импортированы!')
                ))
        except Exception as error:
            self.stderr.write(self.style.ERROR(
                f'Ошибка при импорте данных: {error}'
            ))
