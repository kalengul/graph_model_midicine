"""Модуль команды очистки противопоказаний в БД."""

import traceback

from django.core.management.base import BaseCommand

from contraindications.utils.cleaner import CleanProcessor


class Command(BaseCommand):
    """Команда очистки противопоказаний в БД."""

    help = "Очистить противопоказаний в БД."

    def handle(self, *args, **options):
        """Очистка противопоказания."""
        try:
            CleanProcessor().get_cleaner().clean()
            self.stdout.write(self.style.SUCCESS(
                'Противопоказания удалины успешно!'))
        except Exception:
            traceback.print_exc()
            self.stderr.write(self.style.ERROR(
                'При удалении противопоказаний возникла ошибка!'))
