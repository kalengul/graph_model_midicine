"""Модуль загрузки графов в БД."""

from django.core.management.base import BaseCommand

from graphs.utils.graph_loader import JSONGraphLoader


class Command(BaseCommand):
    """Команда загруки графов в БД."""

    help = 'Загрука графов в БД.'

    def handle(self, *args, **options):
        """Загрука графов в БД."""
        try:
            JSONGraphLoader().load()
            self.stdout.write(self.style.SUCCESS(
                'Графы загружены в БД успешно!'))
        except Exception as error:
            self.stderr.write(self.style.ERROR(
                ('При загрузке графов произошла ошибка!'
                 f'Ошибка: {error}')
            ))
