"""Модуль команды очистки таблицы моделей из drugs."""

from django.core.management.base import BaseCommand

from drugs.utils.cleaner import CleanProcessor


class Command(BaseCommand):
    """Команда очистки таблицы."""

    help = ('Очищает таблицы DrugGroup, Drug, SideEffect, '
            'DrugSideEffect и сбрасывает автоинкремент id')

    def handle(self, *args, **kwargs):
        """Выполнение очистки таблиц."""
        cleaner = CleanProcessor().get_cleaner()
        cleaner.clear_table()
        self.stdout.write(self.style.SUCCESS(
            'Таблицы очищены и id сброшены'))
