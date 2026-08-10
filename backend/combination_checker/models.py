"""
combination_checker/models.py
"""

from django.db import models, transaction
from django.utils import timezone


class CombinationReportManager(models.Manager):
    """
    Управление состоянием CombinationReport.
    """

    def mark_running(
        self,
        report_id: int,
        *,
        total_iterations: int = 0,
    ):
        now = timezone.now()

        return (
            self.filter(pk=report_id)
            .update(
                status=CombinationReport.Status.RUNNING,
                started_at=now,
                finished_at=None,
                duration=None,
                progress=0,
                total_iterations=total_iterations,
                completed_iterations=0,
                checked_combinations=0,
                found_combinations=0,
                current_combination="",
                error_message="",
                updated_at=now,
                is_active=True,
            )
        )

    def update_progress(
        self,
        report_id: int,
        *,
        progress: float,
        checked: int,
        found: int,
    ):
        progress = max(
            0.0,
            min(float(progress), 99.0),
        )

        return (
            self.filter(
                pk=report_id,
                status=CombinationReport.Status.RUNNING,
            )
            .update(
                progress=progress,
                completed_iterations=checked,
                checked_combinations=checked,
                found_combinations=found,
                updated_at=timezone.now(),
            )
        )

    def mark_completed(
        self,
        report_id: int,
        *,
        checked: int,
        found: int,
        result_file: str | None = None,
        error: str = "",
    ):
        now = timezone.now()
        report = self.get(pk=report_id)

        fields = {
            "status": CombinationReport.Status.COMPLETED,
            "progress": 100.0,
            "completed_iterations": checked,
            "checked_combinations": checked,
            "found_combinations": found,
            "finished_at": now,
            "updated_at": now,
            "is_active": False,
            "error_message": error,
            "duration": (
                now - report.started_at
                if report.started_at
                else None
            ),
            "current_combination": "",
        }

        if result_file is not None:
            fields["result_file"] = result_file

        return (
            self.filter(pk=report_id)
            .update(**fields)
        )

    def mark_cancelled(
        self,
        report_id: int,
        *,
        checked: int,
        found: int,
    ):
        now = timezone.now()
        report = self.get(pk=report_id)

        return (
            self.filter(pk=report_id)
            .update(
                status=CombinationReport.Status.CANCELED,
                finished_at=now,
                updated_at=now,
                is_active=False,
                duration=(
                    now - report.started_at
                    if report.started_at
                    else None
                ),
                completed_iterations=checked,
                checked_combinations=checked,
                found_combinations=found,
                current_combination="",
            )
        )
    
    def mark_failed(
        self,
        report_id: int,
        *,
        checked: int,
        found: int,
        error: str,
    ):
        now = timezone.now()
        report = self.get(pk=report_id)

        return (
            self.filter(
                pk=report_id,
                status=CombinationReport.Status.RUNNING,
            )
            .update(
                status=CombinationReport.Status.FAILED,
                progress=0.0,  # либо оставить текущий progress
                completed_iterations=checked,
                checked_combinations=checked,
                found_combinations=found,
                finished_at=now,
                updated_at=now,
                is_active=False,
                error_message=str(error),
                duration=(
                    now - report.started_at
                    if report.started_at
                    else None
                ),
                current_combination="",
            )
        )

    def is_cancelled(
        self,
        report_id: int,
    ) -> bool:
        return (
            self.filter(
                pk=report_id,
                status=CombinationReport.Status.CANCELED,
            )
            .exists()
        )
    
    

    def claim_active(self, report_id):
        with transaction.atomic():
            active_exists = self.filter(
                status=self.model.Status.RUNNING,
                is_active=True,
            ).exclude(
                pk=report_id,
            ).exists()

            if active_exists:
                return False

            updated = self.filter(
                pk=report_id,
                status=self.model.Status.RUNNING,
                is_active=False,
            ).update(
                is_active=True,
            )

            return updated == 1


class CombinationReport(models.Model):
    """
    Отчёт о массовой проверке комбинаций.
    """

    objects = CombinationReportManager()

    class Status(models.TextChoices):
        RUNNING = "running", "В работе"
        COMPLETED = "completed", "Завершён"
        CANCELED = "canceled", "Отменён"
        FAILED = "failed", "Ошибка"

    RANK_FIELDS = (
        ("rang_base", "rang_base"),
        ("rang_f1", "rang_f1"),
        ("rang_f2", "rang_f2"),
        ("rang_freq", "rang_freq"),
        ("rang_m1", "rang_m1"),
        ("rang_m2", "rang_m2"),
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Название отчёта",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RUNNING,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    duration = models.DurationField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=False,
        db_index=True,
    )

    # ----------------------------------------------------------
    # Параметры запуска
    # ----------------------------------------------------------

    max_combination_size = models.PositiveSmallIntegerField(
        default=2,
    )

    rank_name = models.CharField(
        max_length=64,
        choices=RANK_FIELDS,
        default="rang_base",
        db_index=True,
    )

    weight_version_name = models.CharField(
        max_length=255,
        editable=False,
    )

    weight_version_hash = models.CharField(
        max_length=64,
        editable=False,
    )

    weight_version_uploaded_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )

    # ----------------------------------------------------------
    # Прогресс
    # ----------------------------------------------------------

    total_iterations = models.BigIntegerField(
        default=0,
    )

    completed_iterations = models.BigIntegerField(
        default=0,
    )

    checked_combinations = models.BigIntegerField(
        default=0,
    )

    found_combinations = models.BigIntegerField(
        default=0,
    )

    progress = models.FloatField(
        default=0,
    )

    current_combination = models.TextField(
        blank=True,
        default="",
    )

    # ----------------------------------------------------------
    # Результат
    # ----------------------------------------------------------

    result_file = models.CharField(
        max_length=512,
        blank=True,
        default="",
    )

    error_message = models.TextField(
        blank=True,
        default="",
    )

    class Meta:
        ordering = ("-created_at",)

        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=models.Q(
                    is_active=True
                ),
                name="only_one_active_combination_report",
            ),
        ]

        verbose_name = (
            "Отчёт проверки комбинаций"
        )

        verbose_name_plural = (
            "Отчёты проверки комбинаций"
        )

        indexes = [
            models.Index(fields=("status",)),
            models.Index(
                fields=("weight_version_name",)
            ),
            models.Index(fields=("created_at",)),
            models.Index(fields=("rank_name",)),
        ]

    def __str__(self):
        return (
            f"{self.name} "
            f"({self.get_status_display()})"
        )