"""Orchestration of data loading, checking, progress and result storage."""

from __future__ import annotations

from math import comb
from pathlib import Path

from combination_checker.services.loader import DataLoader
from combination_checker.services.progress import ProgressReporter
from combination_checker.services.checker import CombinationChecker
from combination_checker.services.storage import CSVResultWriter


class CombinationGenerator:
    def __init__(
        self,
        calculator,
        report,
        rank_name: str,
        max_size: int,
        output_file: Path,
    ):
        self.calculator = calculator
        self.report = report
        self.rank_name = rank_name
        self.max_size = max_size
        self.output_file = Path(
            output_file
        )

    def run(self):
        progress_reporter = ProgressReporter(
            self.report
        )

        writer = CSVResultWriter(
            self.output_file
        )

        stats = None
        writer_opened = False

        try:
            loader = DataLoader(
                calculator=self.calculator,
                rank_name=self.rank_name,
            )

            dataset = loader.load()

            # Теоретический максимум.
            #
            # Фактически проверенных комбинаций
            # может быть значительно меньше из-за pruning.
            total_iterations = sum(
                comb(dataset.n_drug, size)
                for size in range(
                    2,
                    self.max_size + 1,
                )
                if size <= dataset.n_drug
            )

            progress_reporter.start(
                total_iterations=total_iterations
            )

            writer.open()
            writer_opened = True

            found_counter = 0

            def on_result(result):
                nonlocal found_counter

                found_counter += 1

                writer.write(
                    drug_ids=result.drug_ids,
                    drug_names=result.drug_names,
                    max_rank=result.max_rank,
                )

            def on_progress(checked, pruned):
                if total_iterations <= 0:
                    progress = 100.0
                else:
                    progress = min(
                        99.0,
                        checked
                        * 100.0
                        / total_iterations,
                    )

                progress_reporter.update(
                    progress=progress,
                    checked=checked,
                    found=found_counter,
                    pruned=pruned,
                )

            def is_cancelled():
                return (
                    progress_reporter
                    .is_cancelled()
                )

            checker = CombinationChecker(
                dataset=dataset,
                calculator=self.calculator,
                max_size=self.max_size,
                on_result=on_result,
                on_progress=on_progress,
                is_cancelled=is_cancelled,
            )

            stats = checker.run()

            # Закрываем CSV ДО finish().
            writer.close()
            writer_opened = False

            if not self.output_file.is_file():
                raise RuntimeError(
                    "Result CSV file was not created."
                )

            result_name = (
                self.output_file.name
            )

            progress_reporter.finish(
                checked=stats.checked,
                found=stats.found,
                result_file=result_name,
            )

            return self.output_file

        except InterruptedError:
            if writer_opened:
                writer.close()
                writer_opened = False

            progress_reporter.cancel(
                checked=(
                    stats.checked
                    if stats
                    else 0
                ),
                found=(
                    stats.found
                    if stats
                    else 0
                ),
            )

            if self.output_file.exists():
                self.output_file.unlink()

            return None

        except Exception as exc:
            if writer_opened:
                writer.close()
                writer_opened = False

            progress_reporter.fail(
                exc,
                checked=(
                    stats.checked
                    if stats
                    else 0
                ),
                found=(
                    stats.found
                    if stats
                    else 0
                ),
            )

            if self.output_file.exists():
                self.output_file.unlink()

            raise

        finally:
            if writer_opened:
                writer.close()