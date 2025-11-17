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

DB_PATH="/app/llm.db"

if [ -d "$DB_PATH" ]; then
    echo "Detected directory at $DB_PATH. Replacing it with a SQLite file."
    rm -rf "$DB_PATH"
fi

if [ ! -f "$DB_PATH" ]; then
    touch "$DB_PATH"
    chmod 664 "$DB_PATH"
fi

exec "$@"

