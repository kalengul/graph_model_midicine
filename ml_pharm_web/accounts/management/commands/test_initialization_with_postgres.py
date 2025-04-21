"""Модуль тестовой инициализации."""

import os

from django.core.management.base import BaseCommand
import django
from django.core.management import call_command


class Command(BaseCommand):
    """Команда текстовой инициализации с Postgres."""

    help = 'Вполняет тестовую инициализацию с Postgres.'

    def handle(self, *args, **options):
        """Тестовая инициализация."""
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
        django.setup()

        call_command('makemigrations')
        call_command('migrate')
        call_command('pg_test')
        call_command('clean_medscape')
        call_command('custom_clear')
        call_command('import_data')
        call_command('load_medscape_data')
        call_command('runserver')
