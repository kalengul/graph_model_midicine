import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'medscape_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'medscape.log'),
            'formatter': 'detailed',
            'encoding': 'utf-8'
        },
        'fortran_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'fortran.log'),
            'formatter': 'detailed',
            'encoding': 'utf-8'
        },
        'drugs_file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'drugs.log'),
            'formatter': 'detailed',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'medscape': {
            'handlers': ['medscape_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'fortran': {
            'handlers': ['fortran_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'drugs': {
            'handlers': ['drugs_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    },
}
