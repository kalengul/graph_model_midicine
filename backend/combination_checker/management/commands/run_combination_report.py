"""
combination_checker/management/commands/run_combination_report.py
"""

import logging
logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand

from combination_checker.models import CombinationReport
from combination_checker.services.task_runner import TaskRunner

class Command(BaseCommand):
    help = (
        "Запускает расчёт отчёта комбинаций "
        "в текущем процессе."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "report_id",
            type=int,
        )

    def handle(
        self,
        *args,
        **options,
    ):
        report_id = options["report_id"]

        report = CombinationReport.objects.get(pk=report_id)
        if not report.is_active or report.status != CombinationReport.Status.RUNNING:
            self.stderr.write(
                self.style.ERROR(
                    f"Отчёт #{report_id} не захвачен для выполнения."
                )
            )
            raise CommandError("Report is not active and running.")

        self.stdout.write(f"Запуск расчёта отчёта #{report_id}")

        try:
            TaskRunner().run(report_id)

        except Exception as exc:
            logger.exception("Ошибка выполнения отчёта #%s", report_id)

            self.stderr.write(
                self.style.ERROR(
                    f"Ошибка: {exc}"
                )
            )

            raise

        self.stdout.write(
            self.style.SUCCESS(
                f"Отчёт #{report_id} завершён."
            )
        )
