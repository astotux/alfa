#!/bin/bash

# Функция для обработки сигналов завершения
cleanup() {
    echo "Получен сигнал завершения, останавливаем все сервисы..."
    kill $(jobs -p) 2>/dev/null || true
    wait
    exit 0
}

trap cleanup SIGTERM SIGINT

# Запуск backend
echo "🚀 Запуск backend на порту 8000..."
cd /app/backend/src && python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Небольшая задержка перед запуском следующего сервиса
sleep 2

# Запуск bot
echo "🤖 Запуск bot..."
cd /app/bot && python main.py &
BOT_PID=$!

# Небольшая задержка перед запуском следующего сервиса
sleep 2

# Запуск frontend
echo "🌐 Запуск frontend на порту 5173..."
cd /app/frontend && npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!

echo "Все сервисы запущены!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"

# Ожидание завершения всех процессов
wait