"""Модуль загруки данных MedScape в БД."""

from django.core.management.base import BaseCommand
from medscape_api.json_loader import JSONLoader


class Command(BaseCommand):
    """Команда загрузки данных из json-файлов в БД."""

    help = 'Команда загрузки данных из json-файлов в БД.'

    def handle(self, *args, **options):
        """Загрузка данных из json-файлов в БД."""
        JSONLoader().load_json_medscape()
        self.stdout.write(self.style.SUCCESS(
            'Данные MedScape загружены успешно!'))
