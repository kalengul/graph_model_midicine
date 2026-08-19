FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN groupadd -g 10001 appuser && \
	useradd -u 10001 -g appuser -M -s /sbin/nologin appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . .

RUN chmod +x /app/healthcheck.py

ARG GIT_COMMIT_HASH=unknown
ENV GIT_COMMIT_HASH=${GIT_COMMIT_HASH}
RUN echo "${GIT_COMMIT_HASH}" > /app/.version

RUN mkdir -p /app/logs && chown -R appuser:appuser /app /entrypoint.sh 

USER appuser 

HEALTHCHECK --interval=10s --timeout=4s --retries=3 --start-period=5s \
    CMD python /app/healthcheck.py

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
