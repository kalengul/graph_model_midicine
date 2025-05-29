"""
Модуль команды для импорда данных в БД.

Выполняется в терминале:
python manage.py import_data
"""

import traceback

from django.core.management.base import BaseCommand
from drugs.utils.db_manipulator import DBManipulator
from drugs.utils.loaders import ExcelLoader


class Command(BaseCommand):
    """Команда для импорта данных в БД из файлов."""

    help = 'Экспорта данных из БД в файл.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--txt',
            action='store_true',
            help= 'Указывает, что данными из БД в экспортируются текстовых файлов'
        )

        parser.add_argument(
            '--excel',
            type=str,
            default=None,
            help='Указывает excel-файл для экспорта данных из БД в файл'
        )

    def handle(self, *args, **options):
        """Импорт данных в БД."""
        try:
            txt = options.get('txt')
            excel_path = options.get('excel')
            if txt:
                DBManipulator().export_from_db()
                self.stdout.write(self.style.SUCCESS(
                    'Данные из БД в текстовые файлы успешно экспортированы!'
                ))
            elif excel_path:
                ExcelLoader(excel_path).export_from_db()
                self.stdout.write(self.style.SUCCESS(
                    f'Данные из БД в {excel_path} успешно экспортированы!'
                ))
            elif not excel_path and not txt:
                ExcelLoader().export_from_db()
                self.stdout.write(self.style.SUCCESS(
                    ('Файл для загрузки не указан. Данные экспортированы!'
                     f' из БД в {ExcelLoader.EXCEL_PATH} успешно экспортированы!')
                ))
        except Exception as error:
            traceback.print_exc()
            self.stderr.write(self.style.ERROR(
                f'Ошибка при экспорте данных: {error}'
            ))
