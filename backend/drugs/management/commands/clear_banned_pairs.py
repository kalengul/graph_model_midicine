"""Модуль команды очистки таблицы запрещённых пар."""

from django.core.management.base import BaseCommand

from drugs.utils.cleaner import BannedDrugPairCleanProcessor


class Command(BaseCommand):
    """Команда очистки таблицы."""

    help = 'Очистка таблицы запрещённых пар.'

    def handle(self, *args, **options):
        """Очистка таблицы запрещённых пар."""
        try:
            BannedDrugPairCleanProcessor().get_cleaner().clear_table()
            self.stderr.write(self.style.SUCCESS(
                'Таблица запрещённых пар очищина успешно!'
            ))
        except Exception as error:
            print('error =', error)
            self.stderr.write(self.style.ERROR(
                'При очистке таблицы запрещённых пар произошла ошибка.'
            ))
