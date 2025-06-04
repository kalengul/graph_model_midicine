import os
from pathlib import Path
from django.conf import settings


BASE_DIR = Path(__file__).resolve().parent.parent

# Проверка режима (используется settings.DEBUG)
DEBUG = getattr(settings, 'DEBUG', True)

# Общий форматтер
formatters = {
    'detailed': {
        'format': '{asctime} {levelname} {name} {message}',
        'style': '{',
    },
}

# Хендлеры по умолчанию: всегда лог в консоль
handlers = {
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'detailed'
    },
}

# Добавим файловые хендлеры только если не DEBUG
if not DEBUG:
    log_dir = os.path.join(BASE_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    handlers.update({
        'medscape_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir, 'medscape.log'),
            'formatter': 'detailed',
            'encoding': 'utf-8'
        },
        'fortran_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir, 'fortran.log'),
            'formatter': 'detailed',
            'encoding': 'utf-8'
        },
        'drugs_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir, 'drugs.log'),
            'formatter': 'detailed',
            'encoding': 'utf-8'
        },
        'apilog_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(log_dir, 'apilog.log'),
            'formatter': 'detailed',
            'encoding': 'utf-8'
        },
    })

# Назначим хендлеры по логгерам
loggers = {
    'medscape': {
        'handlers': ['console'] + ([] if DEBUG else ['medscape_file']),
        'level': 'DEBUG',
        'propagate': False
    },
    'fortran': {
        'handlers': ['console'] + ([] if DEBUG else ['fortran_file']),
        'level': 'DEBUG',
        'propagate': False
    },
    'drugs': {
        'handlers': ['console'] + ([] if DEBUG else ['drugs_file']),
        'level': 'DEBUG',
        'propagate': False
    },
    'apilog': {
        'handlers': ['console'] + ([] if DEBUG else ['apilog_file']),
        'level': 'INFO',
        'propagate': False
    },
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': formatters,
    'handlers': handlers,
    'loggers': loggers,
}
