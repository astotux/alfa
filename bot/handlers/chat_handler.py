"""Обработчик текстовых сообщений (чат)"""

from aiogram import Router, F
from aiogram.types import Message
from services.llm_service import get_llm_response
from services.memory_service import memory
from services.db_service import db
from utils.disclaimers import LEGAL_DISCLAIMER
from .keyboards import main_kb
from .sessions import active_requests, user_chat_sessions
from .utils import is_legal_query, get_system_prompt

router = Router()


@router.message(F.text)
async def handle_message(message: Message):
    """Обрабатывает текстовые сообщения пользователей"""
    user_query = message.text.strip()

    # Игнорируем кнопки (на случай дублирования)
    if user_query in ["🗑️ Очистить историю", "📥 Синхронизировать диалог"]:
        return

    telegram_id = message.from_user.id
    
    # Проверяем, есть ли уже активный запрос от этого пользователя
    if active_requests.get(telegram_id, False):
        await message.answer("⏳ Я сейчас занят, думаю как ответить вам на ваш предыдущий запрос...")
        return
    
    # Устанавливаем флаг активного запроса
    active_requests[telegram_id] = True
    
    # Пытаемся получить user_id из БД (может быть None, если пользователь не авторизован)
    user_id = None
    try:
        user_id = await db.get_user_id_by_telegram_id(telegram_id)
    except Exception as e:
        print(f"[ERROR] Ошибка при получении user_id: {e}")
        # Продолжаем работу без сохранения в БД

    # Получаем или создаем chat_id (только для авторизованных пользователей)
    chat_id = None
    if user_id:
        # Пользователь авторизован - работаем с БД
        if telegram_id in user_chat_sessions:
            chat_id = user_chat_sessions[telegram_id].get("chat_id")
        
        # Если нет активного чата, создаем новый
        if not chat_id:
            try:
                # Используем первые 100 символов запроса как заголовок
                title = user_query[:100] if len(user_query) > 0 else "Новый диалог"
                chat_id = await db.create_chat(user_id, title)
                
                # Сохраняем в session
                if telegram_id not in user_chat_sessions:
                    user_chat_sessions[telegram_id] = {}
                user_chat_sessions[telegram_id]["chat_id"] = chat_id
                user_chat_sessions[telegram_id]["user_id"] = user_id
            except Exception as e:
                print(f"[ERROR] Ошибка при создании чата: {e}")
                # Продолжаем работу без сохранения в БД

        # Сохраняем сообщение пользователя в БД
        if chat_id:
            try:
                await db.create_message(chat_id, "user", user_query)
            except Exception as e:
                print(f"[ERROR] Ошибка при сохранении сообщения пользователя: {e}")

    # Отправляем сообщение ожидания
    waiting_message = await message.answer("⏳ Думаю над ответом...")

    # Работаем с памятью (для всех пользователей - авторизованных и неавторизованных)
    context = memory.get_summary(telegram_id)

    # Определяем тип запроса и получаем системный промпт
    is_legal = is_legal_query(user_query)
    system_prompt = get_system_prompt(is_legal)

    try:
        try:
            full_response = await get_llm_response(
                query=user_query,
                context=context,
                system_prompt=system_prompt
            )
        except Exception as e:
            print(f"[ERROR] LLM error: {e}")
            # Удаляем сообщение ожидания
            try:
                await waiting_message.delete()
            except:
                pass
            await message.answer("❌ Не удалось получить ответ. Попробуйте позже.")
            return

        # Добавляем дисклеймер для юридических вопросов
        if is_legal and LEGAL_DISCLAIMER not in full_response:
            response = f"{full_response}\n\n{LEGAL_DISCLAIMER}"
        else:
            response = full_response

        # Сохраняем сообщение ассистента в БД (только для авторизованных пользователей)
        if chat_id and user_id:
            try:
                await db.create_message(chat_id, "assistant", response)
            except Exception as e:
                print(f"[ERROR] Ошибка при сохранении сообщения ассистента: {e}")

        # Сохраняем в память (для всех пользователей)
        memory.add_message(telegram_id, f"Пользователь: {user_query}\nАссистент: {response}")

        # Удаляем сообщение ожидания
        try:
            await waiting_message.delete()
        except:
            pass

        # Отправляем ответ частями (ограничение Telegram — 4096 символов)
        for i in range(0, len(response), 4000):
            await message.answer(response[i:i + 4000], reply_markup=main_kb)
    finally:
        # Сбрасываем флаг активного запроса в любом случае
        active_requests[telegram_id] = False

