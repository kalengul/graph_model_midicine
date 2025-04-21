"""Модуль подключение SQLite."""

import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Команда подключения SQLite."""

    help = 'Запуск с SQLite.'

    def handle(self, *args, **options):
        """Изменения значения окружение для SQLite."""
        os.environ['USE_SQLITE'] = 'True'
        self.stdout.write(self.style.SUCCESS('Подключение к SQLite выполнено'))
