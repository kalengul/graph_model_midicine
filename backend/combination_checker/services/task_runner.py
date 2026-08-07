"""Background runner for combination reports without Celery."""

from __future__ import annotations

import logging
import threading
from pathlib import Path

from ranker.utils.fortran_calculator import FortranCalculator

from combination_checker.models import CombinationReport
from combination_checker.services.generator import CombinationGenerator
from combination_checker.services.report_service import ReportService

logger = logging.getLogger(__name__)


class TaskRunner:
    """
    Запускает один комбинированный отчет в фоновом потоке.

    Флаг базы данных `is_active` является защитой
    от однократного запуска в разных процессах.

    Локальная блокировка процесса предотвращает
    одновременный запуск двух потоков одним
    и тем же процессом Django.
    """

    def __init__(self):
            self.report_service = (
                ReportService()
            )

    def run(self, report: CombinationReport):
        calculator = FortranCalculator()

        filename = self.report_service.build_filename(report)

        generator = CombinationGenerator(
            calculator=calculator,
            report=report,
            rank_name=report.rank_name,
            max_size=report.max_combination_size,
            output_file=filename,
        )

        return generator.run()

    @staticmethod
    def start(report_id: int) -> None:
        def worker():
            try:
                report = CombinationReport.objects.get(pk=report_id)

                if (
                    not report.is_active
                    or report.status != CombinationReport.Status.RUNNING
                ):
                    logger.warning(
                        "Report #%s is not active and running.",
                        report_id,
                    )
                    return

                TaskRunner().run(report)

            except Exception:
                logger.exception(
                    "Ошибка выполнения отчёта #%s",
                    report_id,
                )

        thread = threading.Thread(
            target=worker,
            name=f"combination-report-{report_id}",
            daemon=True,
        )
        thread.start()