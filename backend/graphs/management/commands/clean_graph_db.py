"""Модуль очистки таблицы графов."""

from django.core.management.base import BaseCommand

from graphs.utils.cleaner_graph_db import CleanProcessor


class Command(BaseCommand):
    """Команда очистки таблицы графов."""

    help = 'Очистка таблицы графов в БД.'

    def handle(self, *args, **options):
        """Очистка таблицы графов в БД."""
        try:
            CleanProcessor().get_cleaner().clean()
            self.stdout.write(self.style.SUCCESS(
                'Таблица графов очищина успешно!'
            ))
        except Exception as error:
            print('error = ', error)
            self.stderr.write(self.style.ERROR(
                ('При отистке таблицы графов произошла ошибка.'
                 f'Ошибка: {error}')
            ))
