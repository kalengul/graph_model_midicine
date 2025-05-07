FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py import_data && python manage.py load_medscape_data && gunicorn ml_pharm_web.wsgi:application --bind 0.0.0.0:8000"]