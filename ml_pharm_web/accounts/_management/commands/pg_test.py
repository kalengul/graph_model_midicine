"""Модуль команды подключения PostgreSQL."""

import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Команда подлючение Postgres."""

    help = 'Подключает PostgreSQL'

    def handle(self, *args, **options):
        """Подключение Postgres."""
        os.environ['USE_SQLITE'] = 'False'
        self.stdout.write(self.style.SUCCESS('Switched to PostgreSQL'))
