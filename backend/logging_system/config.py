# logging_system/config.py
import os
import logging
from logging.handlers import RotatingFileHandler
from django.conf import settings

LOG_DIR = settings.LOG_DIR
LOG_FILES = {
    'fortran_calc': 'fortran_calc.log',
    'risk_assessments': 'risk_assessments.log',
}

def get_logger(logger_name: str, log_file: str):
    """
    Возвращает логгер с ротацией.
    logger_name — уникальное имя логгера, например 'fortran_calc'.
    log_file — имя файла внутри LOG_DIR.
    """
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        git_version = os.getenv('GIT_COMMIT_VERSION')
        # git_version = os.getenv('GIT_COMMIT_VERSION') or get_current_commit_hash() or 'N/A'
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '{asctime} | {git_version} | {message}',
            style='{',
            datefmt='%Y-%m-%d %H:%M:%S',
            defaults={'git_version': git_version or 'N/A'},
        )

        handler = RotatingFileHandler(
            os.path.join(LOG_DIR, log_file),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )

        class GitVersionFilter(logging.Filter):
            def __init__(self, git_version):
                super().__init__()
                self.git_version = git_version
            def filter(self, record):
                record.git_version = self.git_version or 'N/A'
                return True

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addFilter(GitVersionFilter(git_version))

    return logger