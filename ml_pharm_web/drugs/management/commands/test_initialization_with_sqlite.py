"""Модуль тестовой инициализации."""

import os

from django.core.management.base import BaseCommand
import django
from django.core.management import call_command


class Command(BaseCommand):
    """Команда текстовой инициализации с SQLite."""

    help = 'Вполняет тестовую инициализацию с SQLite.'

    def handle(self, *args, **options):
        """Тестовая инициализация."""
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ml_pharm_web.settings')
        django.setup()

        call_command('makemigrations')
        call_command('migrate')
        call_command('sqlite_test')
        call_command('clean_medscape')
        call_command('custom_clear')
        call_command('import_data')
        call_command('load_medscape_data')
        call_command('runserver')
