from django.core.management.base import BaseCommand, CommandError

from combination_checker.models import CombinationReport
from combination_checker.services.task_runner import TaskRunner


class Command(BaseCommand):
    help = "Run a combination report synchronously in the current process."

    def add_arguments(self, parser):
        parser.add_argument("report_id", type=int)

    def handle(self, *args, **options):
        report = CombinationReport.objects.get(pk=options["report_id"])
        if not report.is_active or report.status != CombinationReport.Status.RUNNING:
            raise CommandError("Report is not active and running.")
        TaskRunner().run(report.pk)
