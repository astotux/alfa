"""Управление сессиями пользователей"""

# Session для хранения состояния пагинации чатов
# Структура: {telegram_id: {"chats": [...], "current_page": 0, "message_id": ...}}
sync_sessions = {}

# Session для хранения текущего chat_id пользователя
# Структура: {telegram_id: {"chat_id": "...", "user_id": "..."}}
user_chat_sessions = {}

# Отслеживание активных запросов пользователей
# Структура: {telegram_id: True/False}
active_requests = {}

