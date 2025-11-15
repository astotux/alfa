from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from services.llm_service import get_llm_response
from services.memory_service import memory
from services.db_service import db
from utils.disclaimers import LEGAL_DISCLAIMER
from services.db_service import db
import re

router = Router()

# Клавиатура с кнопкой очистки
clear_button = KeyboardButton(text="🗑️ Очистить историю")
main_kb = ReplyKeyboardMarkup(
    keyboard=[[clear_button]],
    resize_keyboard=True,
    one_time_keyboard=False
)

LEGAL_KEYWORDS = ["закон", "юридический", "договор", "суд", "лицензия", "налог", "права", "юрист", "кодекс", "законодательство"]

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

@router.message(F.text == "🗑️ Очистить историю")
async def clear_history(message: Message):
    user_id = message.from_user.id
    memory.clear(user_id)
    await message.answer("✅ История диалога успешно очищена!", reply_markup=main_kb)

@router.message(F.text)
async def handle_message(message: Message):
    user_query = message.text.strip()

    # Игнорируем кнопку (на случай дублирования)
    if user_query == "🗑️ Очистить историю":
        return

    user_id = message.from_user.id
    context = memory.get_summary(user_id)

    # Определяем, юридический ли запрос
    is_legal_query = any(word in user_query.lower() for word in LEGAL_KEYWORDS)

    if is_legal_query:
        system_prompt = (
            "Ты юридический консультант для малого бизнеса. Объясняй законы и нормы простым языком. "
            "Всегда напоминай, что не являешься профессиональным юристом."
        )
    else:
        system_prompt = (
            "Ты эксперт по ведению малого бизнеса. Отвечай профессионально, структурированно и полезно."
        )

    try:
        full_response = await get_llm_response(
            query=user_query,
            context=context,
            system_prompt=system_prompt
        )
    except Exception as e:
        print(f"[ERROR] LLM error: {e}")
        await message.answer("❌ Не удалось получить ответ. Попробуйте позже.")
        return

    # Добавляем дисклеймер для юридических вопросов
    if is_legal_query and LEGAL_DISCLAIMER not in full_response:
        response = f"{full_response}\n\n{LEGAL_DISCLAIMER}"
    else:
        response = full_response

    # Сохраняем в память
    memory.add_message(user_id, f"Пользователь: {user_query}\nАссистент: {response}")

    # Отправляем ответ частями (ограничение Telegram — 4096 символов)
    for i in range(0, len(response), 4000):
        await message.answer(response[i:i + 4000], reply_markup=main_kb)