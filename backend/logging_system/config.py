# backend/logging_system/config.py
import os
import logging
from logging.handlers import RotatingFileHandler

# Директория для логов (относительно backend)
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Файл с логами расчётов
LOG_FILE = os.path.join(LOG_DIR, 'requested_drugs.log')

def get_logger():
    """Настройка логгера с ротацией файлов (10 MB, 5 бэкапов)."""
    logger = logging.getLogger('calculation_api')
    if not logger.handlers:          # избегаем дублирования
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '{asctime} | {message}',
            style='{',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler = RotatingFileHandler(
            LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger