"""
combination_checker/services/task_launcher.py
"""

from __future__ import annotations

import os
import subprocess
import sys


class TaskLauncher:
    """
    Запускает расчёт в отдельном процессе.
    """

    @staticmethod
    def launch(report_id: int) -> None:
        """
        Запускает management command в фоне.
        """

        command = [
            sys.executable,
            "manage.py",
            "run_combination_report",
            str(report_id),
        ]

        env = os.environ.copy()

        subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
            start_new_session=True,
        )
