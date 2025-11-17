# Альфа-помощник (Alfa-Helper)

Универсальный AI-помощник для владельцев микро-бизнеса, предоставляющий поддержку через веб-приложение и Telegram-бот. Система помогает предпринимателям с различными бизнес-задачами: от стратегического планирования до работы с документами и анализа рисков.

## 📋 Описание проекта

**Альфа-помощник** — это комплексная платформа, состоящая из трех основных компонентов:

1. **Backend API** — REST API на FastAPI для управления пользователями, чатами и интеграции с LLM
2. **Telegram Bot** — бот для взаимодействия с пользователями через Telegram
3. **Frontend** — веб-приложение на React для работы с чатами и анализами

## 🏗️ Архитектура проекта

```
alfa/
├── backend/          # FastAPI backend
├── bot/              # Telegram bot (aiogram)
└── frontend/         # React frontend
```

## 🛠️ Технологический стек

### Backend
- **Python 3.12+**
- **FastAPI** — современный веб-фреймворк для создания API
- **SQLAlchemy** — ORM для работы с базой данных
- **SQLite** — база данных (файл `llm.db`)
- **another-fastapi-jwt-auth** — JWT аутентификация
- **bcrypt** — хеширование паролей
- **httpx** — асинхронные HTTP-запросы к OpenRouter API
- **uvicorn** — ASGI сервер
- **pydantic-settings** — управление настройками

### Bot (Telegram)
- **Python 3.10+**
- **aiogram 3.10.0** — фреймворк для создания Telegram-ботов
- **OpenAI SDK** — клиент для работы с OpenRouter API
- **Pillow** — генерация изображений истории чата
- **PyMuPDF** — обработка PDF документов
- **python-docx** — обработка DOCX документов
- **aiosqlite** — асинхронная работа с SQLite
- **python-dotenv** — загрузка переменных окружения

### Frontend
- **React 19.2.0** — библиотека для создания пользовательских интерфейсов
- **TypeScript 5.9.3** — типизированный JavaScript
- **Vite 7.2.2** — сборщик и dev-сервер
- **Tailwind CSS 4.1.17** — utility-first CSS фреймворк
- **React Router 7.9.6** — маршрутизация
- **TanStack Query 5.90.9** — управление серверным состоянием
- **React Hook Form 7.66.0** — управление формами
- **Zod 4.1.12** — валидация схем
- **Axios** — HTTP-клиент
- **React Markdown** — рендеринг markdown
- **Radix UI** — компоненты UI (Dialog, Dropdown, Tooltip и др.)
- **Sonner** — уведомления (toast)
- **Lucide React** — иконки

### LLM и AI
- **OpenRouter API** — агрегатор LLM моделей
- **Модель**: `tngtech/deepseek-r1t2-chimera:free`
- Поддержка стриминга ответов (Server-Sent Events)

## 📦 Установка и запуск

### Требования

- Python 3.10+ (для бота) и 3.12+ (для backend)
- Node.js 18+ и npm
- uv (менеджер пакетов Python)

### Backend

1. Перейдите в директорию `backend/`
2. Создайте файл `.env` и заполните переменные окружения (см. выше)

3. Установите uv (если еще не установлен):
   ```bash
   pip install uv
   ```

4. Установите зависимости:
   ```bash
   uv sync
   ```

5. Запустите сервер:
   ```bash
   uv run src/main.py
   ```

   Сервер будет доступен по адресу: `http://127.0.0.1:8000`

### Bot (Telegram)

1. Перейдите в директорию `bot/`
2. Создайте файл `.env` и заполните переменные окружения (см. выше)

3. Установите зависимости:
   ```bash
   uv sync
   ```

4. Запустите бота:
   ```bash
   uv run bot
   ```

### Frontend

1. Перейдите в директорию `frontend/`
2. Установите зависимости:
   ```bash
   npm install
   ```

3. (Опционально) Создайте файл `.env` с переменными окружения (см. выше)

4. Запустите dev-сервер:
   ```bash
   npm run dev
   ```

   Приложение будет доступно по адресу: `http://localhost:5173`

5. Соберите production версию:
   ```bash
   npm run build
   ```

## 🚢 Запуск через Docker и Docker Compose

> Перед сборкой создайте файлы `.env` в директориях `backend/`, `bot/` и `frontend/`. Ниже приведены минимальные примеры.

### Примеры переменных окружения

`backend/.env`
```
DATABASE_URL=sqlite:///./llm.db
authjwt_secret_key=change-me
OPENROUTER_API_KEY=your_openrouter_key
```

`bot/.env`
```
TELEGRAM_TOKEN=your_telegram_token
OPENROUTER_API_KEY=your_openrouter_key
DATABASE_PATH=/data/llm.db
```

`frontend/.env`
```
VITE_API_URL=http://backend:8000
```

### Сборка и запуск

1. Соберите и запустите все сервисы:
   ```
   docker compose up --build
   ```
2. После успешного запуска сервисы будут доступны по адресам:
   - Backend API — `http://localhost:8000`
   - Frontend — `http://localhost:5173`
3. Файл `llm.db` из `backend/` монтируется в контейнеры `backend` и `bot`, поэтому данные SQLite остаются на хосте и общие для обоих сервисов.

При необходимости можно собрать образы по отдельности:

- Backend: `docker build -f backend/Dockerfile -t alfa-backend .`
- Bot: `docker build -f bot/Dockerfile -t alfa-bot .`
- Frontend: `docker build -f frontend/Dockerfile -t alfa-frontend .`

После сборки запускайте контейнеры с нужными переменными окружения или `.env` файлами.

## 🗄️ База данных

Проект использует **SQLite** базу данных (`llm.db`), которая находится в директории `backend/`. База данных содержит следующие таблицы:

- **users** — пользователи системы (username, email, hashed_password, telegram_id)
- **chats** — чаты пользователей (id, title, userId, chatType, createdAt, updatedAt)
- **messages** — сообщения в чатах (id, chatId, role, content, createdAt)
- **sync_tokens** — токены для синхронизации между веб-приложением и ботом

## 🔑 Основные функции

### Веб-приложение
- Регистрация и авторизация пользователей
- Создание и управление чатами (general и risk_vision)
- Стриминг ответов от LLM в реальном времени
- Отображение истории сообщений с поддержкой markdown
- Анализ рисков бизнес-идей (RiskVision)
- Синхронизация с Telegram-ботом через токены

### Telegram Bot
- Текстовые сообщения с AI-помощником
- Обработка PDF и DOCX документов
- Синхронизация чатов с веб-приложением
- Генерация изображений истории чата
- Управление памятью диалогов

## 📁 Структура проекта

### Backend (`backend/src/`)
```
backend/src/
├── api/              # API endpoints (auth, chat, llm, user, sync_token)
├── auth/              # JWT аутентификация и зависимости
├── common/            # Общие настройки (config)
├── database/          # Настройка подключения к БД
├── models/            # SQLAlchemy модели (User, Chat, Message, SyncToken)
├── schemas/           # Pydantic схемы для валидации
└── services/          # Бизнес-логика (llm_service)
```

### Bot (`bot/`)
```
bot/
├── handlers/          # Обработчики сообщений и callback'ов
│   ├── start_handler.py      # Команда /start
│   ├── button_handlers.py    # Обработка кнопок
│   ├── callback_handlers.py  # Callback запросы
│   ├── chat_handler.py       # Текстовые сообщения
│   ├── document_handler.py   # Обработка документов
│   └── utils.py              # Утилиты (промпты)
├── services/          # Сервисы
│   ├── db_service.py         # Работа с БД
│   ├── llm_service.py        # Интеграция с LLM
│   ├── memory_service.py     # Управление памятью
│   ├── pdf_service.py        # Обработка PDF
│   └── chat_image_service.py # Генерация изображений
└── utils/             # Утилиты
```

### Frontend (`frontend/src/`)
```
frontend/src/
├── app/               # Главный компонент приложения
├── features/           # Функциональные компоненты
│   ├── auth/          # Авторизация
│   └── chat/          # Чат и сообщения
├── pages/              # Страницы приложения
├── shared/             # Общие компоненты
│   ├── api/           # API клиент и сервисы
│   ├── config/        # Конфигурация
│   ├── hooks/         # React хуки
│   ├── types/         # TypeScript типы
│   └── ui/            # UI компоненты
└── widgets/           # Виджеты (Layout, Sidebar, Header)
```

## 🔄 Синхронизация между веб-приложением и ботом

Пользователи могут синхронизировать свои чаты между веб-приложением и Telegram-ботом:
1. В веб-приложении генерируется токен синхронизации
2. Пользователь отправляет токен боту через ссылку, генерируемую на сайте
3. Бот привязывает Telegram аккаунт к пользователю
4. Чаты становятся доступны в обоих интерфейсах

## 📝 API Endpoints

### Auth
- `POST /auth/register` — регистрация пользователя
- `POST /auth/login` — вход в систему
- `POST /auth/refresh` — обновление токена

### Chat
- `POST /chat` — создание нового чата
- `GET /chat` — получение списка чатов
- `GET /chat/{chat_id}` — получение чата с сообщениями
- `DELETE /chat/{chat_id}` — удаление чата
- `POST /message` — создание сообщения

### LLM
- `GET /api/stream` — стриминг ответа от LLM (SSE)
- `POST /api/chat` — простой запрос к LLM

### User
- `GET /user/profile` — получение профиля пользователя

### Sync Token
- `GET /sync-token` — получение токена синхронизации