"""Обработчик команды /start"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from services.db_service import db
from .keyboards import main_kb

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message):
    """Обрабатывает /start и /start <токен>"""
    text = message.text or ""
    parts = text.split(maxsplit=1)
    token = parts[1] if len(parts) > 1 else None

    if token:
        try:
            # Ищем пользователя по токену
            user_id = await db.get_user_by_token(token)
            if user_id:
                telegram_id = message.from_user.id
                await db.update_telegram_id(user_id, telegram_id)
                await message.answer(
                    "Аккаунт успешно привязан к Telegram!\n\n"
                    "Теперь вы можете пользоваться всеми функциями ИИ-помощника.",
                    reply_markup=main_kb
                )
            else:
                await message.answer(
                    "Неверная или устаревшая ссылка синхронизации.\n"
                    "Пожалуйста, убедитесь, что вы перешли по корректной ссылке."
                )
        except Exception as e:
            print(f"[ERROR] Ошибка при синхронизации: {e}")
            await message.answer(
                "⚠Произошла ошибка при привязке аккаунта. Попробуйте позже."
            )
    else:
        # Обычный старт без токена
        await message.answer(
            "👋 Привет! Я ваш ИИ-помощник для микро-бизнеса.\n\n"
            "🔹 Генерирую тексты: документы, посты, письма\n"
            "🔹 Объясняю законы и нормы\n"
            "🔹 Отвечаю на любые бизнес-вопросы\n"
            "🔹 Редактирую PDF-документы\n\n"
            "Просто напишите запрос или отправьте PDF!",
            reply_markup=main_kb
        )

