#!/bin/bash
set -e

python manage.py migrate

python manage.py collectstatic --noinput

echo "Подгрузка данных..."

python manage.py custom_clear

python manage.py clean_medscape

python manage.py import_data

python manage.py load_medscape_data

echo "Подгрузка данных закончена!"

exec gunicorn ml_pharm_web.wsgi:application --bind 0.0.0.0:8000