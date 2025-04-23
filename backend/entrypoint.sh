#!/bin/bash
set -e

python manage.py migrate

python manage.py collectstatic --noinput

python manage.py import_data

python manage.py load_medscape_data

exec gunicorn ml_pharm_web.wsgi:application --bind 0.0.0.0:8000
