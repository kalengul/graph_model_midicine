import cProfile
import pstats
import io
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from combination_checker.models import CombinationReport
from combination_checker.services.task_runner import TaskRunner

class Command(BaseCommand):
    help = "Run combination report with profiling"

    def add_arguments(self, parser):
        parser.add_argument("report_id", type=int)
        parser.add_argument(
            "--profile",
            action="store_true",
            help="Enable cProfile and save stats to file",
        )
        parser.add_argument(
            "--profile-output",
            type=str,
            default="profile_stats.prof",
            help="Path to save profiling data",
        )

    def handle(self, *args, **options):
        report_id = options["report_id"]
        report = CombinationReport.objects.get(pk=report_id)
        if not report.is_active or report.status != CombinationReport.Status.RUNNING:
            raise CommandError("Report is not active and running.")

        if options["profile"]:
            profiler = cProfile.Profile()
            profiler.enable()
            try:
                TaskRunner().run(report)
            finally:
                profiler.disable()
                # Сохраняем бинарный файл
                output_path = Path(options["profile_output"])
                profiler.dump_stats(str(output_path))
                self.stdout.write(f"Profile saved to {output_path}")

                # Печатаем топ-20 функций в консоль
                s = io.StringIO()
                ps = pstats.Stats(profiler, stream=s).sort_stats("cumtime")
                ps.print_stats(20)
                self.stdout.write(s.getvalue())
        else:
            TaskRunner().run(report)