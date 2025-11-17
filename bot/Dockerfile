FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    DATABASE_PATH=/data/llm.db

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        libgl1 \
        libglib2.0-0 \
        fontconfig \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY bot/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

COPY bot/.env ./.env
COPY bot/ .

COPY bot/entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

# TELEGRAM_TOKEN and DATABASE_PATH must be provided via environment variables.

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "-m", "main"]

