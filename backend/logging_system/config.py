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
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '{asctime} | {git_version} | {message}',
            style='{',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        handler = RotatingFileHandler(
            os.path.join(LOG_DIR, log_file),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        class GitVersionFilter(logging.Filter):
            def filter(self, record):
                record.git_version = git_version
                return True

        logger.addFilter(GitVersionFilter())

    return logger