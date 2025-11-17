FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first to leverage Docker layer caching.
COPY backend/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application source.
COPY backend/.env ./.env
COPY backend/src ./src
COPY backend/llm.db ./llm.db
COPY backend/entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

