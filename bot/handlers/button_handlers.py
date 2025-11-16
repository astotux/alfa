"""Обработчики кнопок клавиатуры"""

from aiogram import Router, F
from aiogram.types import Message
from services.memory_service import memory
from services.db_service import db
from .keyboards import main_kb, build_chats_keyboard
from .sessions import sync_sessions, user_chat_sessions

router = Router()


@router.message(F.text == "🆕 Новый диалог")
async def clear_history(message: Message):
    """Обрабатывает нажатие на кнопку 'Очистить историю'"""
    telegram_id = message.from_user.id
    memory.clear(telegram_id)
    
    # Очищаем текущий chat_id из session (будет создан новый при следующем сообщении)
    if telegram_id in user_chat_sessions:
        del user_chat_sessions[telegram_id]
    
    await message.answer("✅ История диалога успешно очищена!", reply_markup=main_kb)


@router.message(F.text == "📥 Список чатов")
async def sync_dialog(message: Message):
    """Показывает список диалогов для синхронизации с пагинацией"""
    telegram_id = message.from_user.id
    
    try:
        # Получаем user_id по telegram_id
        user_id = await db.get_user_id_by_telegram_id(telegram_id)
        
        if not user_id:
            await message.answer(
                "⚠️ Ваш аккаунт не привязан к системе.\n"
                "Привяжите аккаунт через наш сайт!",
                reply_markup=main_kb
            )
            return
        
        # Получаем список чатов пользователя
        chats = await db.get_user_chats(user_id)
        
        if not chats:
            await message.answer(
                "📭 У вас пока нет сохранённых диалогов в системе.",
                reply_markup=main_kb
            )
            return
        
        # Сохраняем чаты в session
        reply_markup = build_chats_keyboard(chats, 0)
        
        sent_message = await message.answer(
            "📋 Выберите диалог для синхронизации:",
            reply_markup=reply_markup
        )
        
        # Сохраняем состояние в session
        sync_sessions[telegram_id] = {
            "chats": chats,
            "current_page": 0,
            "message_id": sent_message.message_id
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Ошибка при получении диалогов: {e}")
        print(f"[ERROR] Детали: {error_details}")
        await message.answer(
            f"❌ Не удалось загрузить список диалогов.\n\nОшибка: {str(e)}\n\nПопробуйте позже.",
            reply_markup=main_kb
        )

