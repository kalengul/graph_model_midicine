"""Progress and lifecycle state for a combination report."""

from __future__ import annotations

from combination_checker.models import CombinationReport


class ProgressReporter:
    def __init__(self, report):
        self.report = report
        self._last_progress = -1.0

    def start(self, *, total_iterations: int):
        CombinationReport.objects.mark_running(
            self.report.pk,
            total_iterations=total_iterations,
        )
        self._last_progress = 0.0

    def update(self, *, progress: float, checked: int, found: int):
        progress = max(0.0, min(float(progress), 99.0))
        if progress == self._last_progress:
            return
        self._last_progress = progress
        CombinationReport.objects.update_progress(
            self.report.pk,
            progress=progress,
            checked=checked,
            found=found,
        )

    def finish(self, *, checked: int, found: int, result_file=None):
        CombinationReport.objects.mark_completed(
            self.report.pk,
            checked=checked,
            found=found,
            result_file=result_file,
        )

    def fail(self, exc, *, checked: int, found: int):
        CombinationReport.objects.mark_failed(
            self.report.pk,
            checked=checked,
            found=found,
            error=str(exc),
        )

    def cancel(self, *, checked: int, found: int):
        CombinationReport.objects.mark_cancelled(
            self.report.pk,
            checked=checked,
            found=found,
        )

    def is_cancelled(self):
        return CombinationReport.objects.is_cancelled(self.report.pk)
