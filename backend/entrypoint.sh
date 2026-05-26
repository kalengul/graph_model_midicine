#!/bin/bash
set -e

if [ "$GIT_COMMIT_HASH" = "unknown" ]; then
    echo "⚠️  WARNING: GIT_COMMIT_HASH is not set, version unknown" >&2
fi

echo "Running migrations..."
python manage.py migrate --noinput

exec gunicorn ml_pharm_web.wsgi:application --bind 0.0.0.0:8000
