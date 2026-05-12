FROM docker.io/library/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WIKI_SOURCE_DIR=/app/knowledge \
    WIKI_RAW_DIR=/app/knowledge/raw \
    WIKI_OUTPUT_DIR=/app/knowledge/wiki \
    CODEX_COMMAND=codex \
    CODEX_SHELL=powershell \
    CODEX_TIMEOUT_SECONDS=900 \
    CODEX_SOURCE_CHAR_LIMIT=0 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /app/knowledge/raw /app/knowledge/wiki

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT}"]
