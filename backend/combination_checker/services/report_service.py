"""
combination_checker/services/report_service.py
"""

from __future__ import annotations

from pathlib import Path

from django.conf import settings

from combination_checker.models import CombinationReport
from logging_system.models import SystemState


class ReportService:
    """
    Сервис работы с CombinationReport и файлами результатов.
    """

    REPORT_DIR = (
        Path(settings.BASE_DIR)
        / "combination_checker"
        / "reports"
    )

    def __init__(self):
        self.REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # CREATE
    # ==========================================================

    def create(
        self,
        *,
        max_combination_size: int,
        rank_name: str,
        name: str = "",
    ) -> CombinationReport:

        state = SystemState.get_current_state()

        if not name:
            name = (
                f"Combinations "
                f"{max_combination_size}"
            )

        return CombinationReport.objects.create(
            name=name,
            max_combination_size=max_combination_size,
            rank_name=rank_name,
            weight_version_name=(
                state.weights_file_name or ""
            ),
            weight_version_hash=(
                state.weights_file_hash or ""
            ),
            weight_version_uploaded_at=(
                state.weights_file_uploaded_at
            ),
            status=CombinationReport.Status.RUNNING,
            progress=0,
            completed_iterations=0,
            checked_combinations=0,
            found_combinations=0,
            is_active=False,
        )

    # ==========================================================
    # GET
    # ==========================================================

    def get(self, report_id: int) -> CombinationReport:
        return CombinationReport.objects.get(pk=report_id)

    def latest(self):
        return (
            CombinationReport.objects.filter(
                status=CombinationReport.Status.COMPLETED
            )
            .order_by("-finished_at")
            .first()
        )
    
    def latest_running(self):
        return (
            CombinationReport.objects
            .filter(
                status=CombinationReport.Status.RUNNING,
                is_active=True,
            )
            .order_by("-started_at")
            .first()
        )

    # ==========================================================
    # LIST
    # ==========================================================

    def list_reports(self):
        return (
            CombinationReport.objects
            .order_by("-created_at")
        )

    # ==========================================================
    # FILES
    # ==========================================================

    def build_filename(
        self,
        report: CombinationReport,
        extension: str = "csv",
    ) -> Path:
        """
        Создаёт безопасное имя файла результата.
        """

        self.REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        safe_weight_name = "_".join(
            part
            for part in report.weight_version_name
            .replace("\\", "/")
            .split("/")
            if part
        ) or "unknown"

        filename = (
            f"report_{report.pk}"
            f"_weights_{safe_weight_name}"
            f"_{report.created_at:%Y%m%d_%H%M%S}"
            f".{extension.lstrip('.')}"
        )

        return self.REPORT_DIR / filename

    def get_download_path(
        self,
        report: CombinationReport,
    ) -> Path | None:
        """
        Возвращает полный путь к результату.

        result_file содержит только имя файла.
        """

        if not report.result_file:
            return None

        file_path = (
            self.REPORT_DIR / report.result_file
        ).resolve()

        reports_dir = self.REPORT_DIR.resolve()

        try:
            file_path.relative_to(reports_dir)
        except ValueError:
            return None

        return file_path

    def file_exists(
        self,
        report: CombinationReport,
    ) -> bool:
        path = self.get_download_path(report)

        return (
            path is not None
            and path.is_file()
        )

    def delete_file(
        self,
        report: CombinationReport,
    ):
        path = self.get_download_path(report)

        if path is not None and path.exists():
            path.unlink()

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(
        self,
        report: CombinationReport,
        *,
        delete_file: bool = True,
    ):
        if delete_file:
            self.delete_file(report)

        report.delete()

    def delete_old(
        self,
        *,
        keep_last: int = 10,
    ):
        reports = (
            CombinationReport.objects
            .order_by("-created_at")
        )

        for report in reports[keep_last:]:
            self.delete(report)