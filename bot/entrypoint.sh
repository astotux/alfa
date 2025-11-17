#!/bin/sh
set -e

if [ -f .env ]; then
    TMP_ENV="$(mktemp)"
    tr -d '\r' < .env > "$TMP_ENV"
    set -a
    . "$TMP_ENV"
    set +a
    rm -f "$TMP_ENV"
fi

DEFAULT_DB_PATH="/data/llm.db"

if [ -n "$DATABASE_PATH" ]; then
    # Заменяем windows-слеши на unix-слеши.
    DATABASE_PATH="$(printf '%s' "$DATABASE_PATH" | sed 's#\\#/#g')"
fi

if [ -z "$DATABASE_PATH" ] || [ ! -e "$DATABASE_PATH" ]; then
    DATABASE_PATH="$DEFAULT_DB_PATH"
fi

export DATABASE_PATH

exec "$@"

