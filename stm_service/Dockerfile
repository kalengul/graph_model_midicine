FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Если модель лежит в папке models, скопировать ее (лучше смонтировать через volume)
# Но можно и скопировать, если модель не слишком большая.
# Для больших моделей лучше использовать volume или загружать при старте из сети.

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]