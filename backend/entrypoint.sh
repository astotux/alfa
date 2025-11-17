#!/bin/sh
set -e

if [ -f .env ]; then
    TMP_ENV="$(mktemp)"
    # Удаляем windows-переносы строк, чтобы pydantic корректно парсил значения.
    tr -d '\r' < .env > "$TMP_ENV"
    set -a
    . "$TMP_ENV"
    set +a
    rm -f "$TMP_ENV"
fi

exec "$@"

