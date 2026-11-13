#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from logging_system.utils.get_current_commit_hash import get_current_commit_hash


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ml_pharm_web.settings')

    # Поставить актуальный хэш
    if not os.getenv('GIT_COMMIT_VERSION'):
        os.environ['GIT_COMMIT_VERSION'] = get_current_commit_hash() or 'N/A'

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
