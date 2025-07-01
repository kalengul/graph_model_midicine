"""Модуль загрузки запрещённых пар ЛС."""

import os

from django.core.management.base import BaseCommand
from django.conf import settings

from drugs.utils.banned_pairs_loader import CSVBannedPairLoader


class Command(BaseCommand):
    """Команда загрузки запрещённых пар."""

    help = """Загрузка запрещённых пар ЛС."""
    BANNED_PAIRS_FILE_NAME = 'banned_pairs.csv'

    def handle(self, *args, **options):
        """Загрузка запрещённых пар."""
        try:
            CSVBannedPairLoader(
                os.path.join(settings.TXT_DB_PATH,
                            self.BANNED_PAIRS_FILE_NAME)
            ).load_to_db()
            self.stdout.write(
                self.style.SUCCESS('Запрещённые пары ЛС загружены успешно!'))
        except Exception as error:
            print('error =', error)
            self.stderr.write(
                self.style.ERROR(
                    'При загрузка запрещённы пар ЛС возникла ошибка'))
