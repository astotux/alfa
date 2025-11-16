# Базовый образ с Python
FROM python:3.11-slim

# Установка Node.js и необходимых утилит
RUN apt-get update && apt-get install -y \
    curl \
    bash \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование и установка зависимостей backend
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Копирование и установка зависимостей bot
COPY bot/requirements.txt /app/bot/
RUN pip install --no-cache-dir -r /app/bot/requirements.txt

# Копирование и установка зависимостей frontend
COPY frontend/package.json frontend/package-lock.json /app/frontend/
RUN cd /app/frontend && npm ci

# Копирование исходного кода
COPY backend/ /app/backend/
COPY bot/ /app/bot/
COPY frontend/ /app/frontend/

# Копирование скрипта запуска
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Экспонирование портов
EXPOSE 8000 5173

# Запуск скрипта
CMD ["/app/start.sh"]