"""Модуль команды загрузки противопоказаний в БД."""

from django.core.management.base import BaseCommand

from contraindications.utils.loader import LoadAndBuildDrugContraindications


class Command(BaseCommand):
    """Команда загрузки противопоказания из локального JSON файла."""

    help = "Загрузить противопоказания из локального JSON файла."

    def handle(self, *args, **options):
        """Загрузка противопоказания ЛС."""
        try:
            LoadAndBuildDrugContraindications().load()
            self.stdout.write(self.style.SUCCESS(
                'Противопоказания загружены и связаны с ЛС успешно!'))
        except Exception as error:
            print('Ошибка загрузки противопоказаний:', error)
            self.stderr.write(self.style.ERROR(
                'При загрузки противопоказаний возникла ошибка!'))
