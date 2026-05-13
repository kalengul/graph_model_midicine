FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG GIT_COMMIT_HASH=unknown
RUN echo "${GIT_COMMIT_HASH}" > /app/.version

RUN python manage.py collectstatic --noinput

CMD python manage.py migrate && \
    gunicorn ml_pharm_web.wsgi:application --bind 0.0.0.0:8000
