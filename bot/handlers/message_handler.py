from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from services.llm_service import get_llm_response
from services.memory_service import memory  # ← импортируем ГОТОВЫЙ экземпляр
from utils.disclaimers import LEGAL_DISCLAIMER
import re

router = Router()

# Клавиатура с кнопкой очистки
clear_button = KeyboardButton(text="🗑️ Очистить историю")
main_kb = ReplyKeyboardMarkup(
    keyboard=[[clear_button]],
    resize_keyboard=True,
    one_time_keyboard=False
)

LEGAL_KEYWORDS = ["закон", "юридический", "договор", "суд", "лицензия", "налог", "права", "юрист"]

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я ваш Альфа-помощник для микро-бизнеса.\n"
        "Могу:\n"
        "• Генерировать документы и маркетинговые тексты\n"
        "• Объяснять законы и нормы\n"
        "• Отвечать на бизнес-вопросы\n"
        "• Редактировать PDF-документы\n\n"
        "Просто напишите свой запрос или отправьте PDF!",
        reply_markup=main_kb
    )

@router.message(F.text == "🗑️ Очистить историю")
async def clear_history(message: Message):
    user_id = message.from_user.id
    memory.clear(user_id)
    await message.answer("✅ История диалога успешно очищена!", reply_markup=main_kb)

@router.message(F.text)
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_query = message.text

    # Пропускаем обработку, если это кнопка очистки (на всякий случай)
    if user_query == "🗑️ Очистить историю":
        return

    context = memory.get_summary(user_id)
    is_legal_query = any(word in user_query.lower() for word in LEGAL_KEYWORDS)

    if is_legal_query:
        system_prompt = (
            "Ты юридический консультант для малого бизнеса. Объясняй законы и нормы простым языком. "
            "Всегда напоминай, что не являешься профессиональным юристом."
            "Если пользователь говорит, что скинет документ, ты не должен отказывать ему в этом, для тебя мы переформатируем документ в текст"
        )
    else:
        system_prompt = (
            "Ты эксперт по ведению малого бизнеса. Отвечай профессионально, структурированно и полезно."
            "Если пользователь говорит, что скинет документ, ты не должен отказывать ему в этом, для тебя мы переформатируем документ в текст"
        )

    full_response = await get_llm_response(
        query=user_query,
        context=context,
        system_prompt=system_prompt
    )

    if is_legal_query and LEGAL_DISCLAIMER not in full_response:
        response = f"{full_response}\n\n{LEGAL_DISCLAIMER}"
    else:
        response = full_response

    memory.add_message(user_id, f"Пользователь: {user_query}\nАссистент: {response}")

    # Отправка длинных ответов частями
    for i in range(0, len(response), 4000):
        await message.answer(response[i:i+4000], reply_markup=main_kb)