import os
from pathlib import Path
from django.conf import settings


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
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed'
        },
        **({} if settings.DEBUG else { 
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
            },
            'apilog_file': {
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'logs', 'apilog.log'),
                'formatter': 'detailed',
                'encoding': 'utf-8'
            },
        })
    },
    'loggers': {
        'medscape': {
            'handlers': ['console'] if settings.DEBUG else ['medscape_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'fortran': {
            'handlers': ['console'] if settings.DEBUG else ['fortran_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'drugs': {
            'handlers': ['console'] if settings.DEBUG else ['drugs_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'apilog': {
            'handlers': ['console'] if settings.DEBUG else ['apilog_file', 'console'],
            'level': 'INFO',
            'propagate': False
        },
    },
}
