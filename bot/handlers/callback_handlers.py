"""Обработчики callback запросов"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from services.memory_service import memory
from services.db_service import db
from .keyboards import build_chats_keyboard
from .sessions import sync_sessions, user_chat_sessions

router = Router()


@router.callback_query(F.data == "sync_page_info")
async def sync_page_info_callback(callback: CallbackQuery):
    """Обрабатывает нажатие на кнопку с информацией о странице (неактивная кнопка)"""
    await callback.answer()


@router.callback_query(F.data.startswith("sync_page_"))
async def sync_page_callback(callback: CallbackQuery):
    """Обрабатывает переключение страниц в списке диалогов"""
    # Игнорируем кнопку с информацией о странице
    if callback.data == "sync_page_info":
        return
    
    telegram_id = callback.from_user.id
    page = int(callback.data.replace("sync_page_", ""))
    
    # Получаем состояние из session
    if telegram_id not in sync_sessions:
        await callback.answer("❌ Сессия истекла. Нажмите кнопку синхронизации снова.", show_alert=True)
        return
    
    session = sync_sessions[telegram_id]
    chats = session["chats"]
    
    # Обновляем страницу в session
    session["current_page"] = page
    
    # Строим новую клавиатуру
    reply_markup = build_chats_keyboard(chats, page)
    
    await callback.answer()
    await callback.message.edit_text(
        "📋 Выберите диалог для синхронизации:",
        reply_markup=reply_markup
    )


@router.callback_query(F.data == "start_new_chat")
async def start_new_chat_callback(callback: CallbackQuery):
    """Обрабатывает нажатие на кнопку 'Начать новый диалог'"""
    telegram_id = callback.from_user.id
    
    # Очищаем память пользователя
    memory.clear(telegram_id)
    
    # Очищаем текущий chat_id из session (будет создан новый при следующем сообщении)
    if telegram_id in user_chat_sessions:
        del user_chat_sessions[telegram_id]
    
    # Очищаем session синхронизации
    if telegram_id in sync_sessions:
        del sync_sessions[telegram_id]
    
    await callback.answer("✅ Новый диалог начат!")
    await callback.message.edit_text(
        "✅ Новый диалог начат!\n\n"
        "История предыдущего диалога очищена. Вы можете начать новый разговор."
    )


@router.callback_query(F.data.startswith("sync_chat_"))
async def sync_chat_callback(callback: CallbackQuery):
    """Обрабатывает выбор диалога для синхронизации"""
    chat_id = callback.data.replace("sync_chat_", "")
    telegram_id = callback.from_user.id
    
    try:
        # Получаем сообщения из выбранного чата
        messages = await db.get_chat_messages(chat_id)
        
        if not messages:
            await callback.answer("Диалог пуст", show_alert=True)
            await callback.message.delete()
            # Очищаем session
            if telegram_id in sync_sessions:
                del sync_sessions[telegram_id]
            return
        
        # Синхронизируем память с сообщениями из диалога
        memory.sync_from_messages(telegram_id, messages)
        
        # Устанавливаем текущий chat_id в session
        user_id = await db.get_user_id_by_telegram_id(telegram_id)
        if user_id:
            if telegram_id not in user_chat_sessions:
                user_chat_sessions[telegram_id] = {}
            user_chat_sessions[telegram_id]["chat_id"] = chat_id
            user_chat_sessions[telegram_id]["user_id"] = user_id
        
        # Очищаем session после выбора
        if telegram_id in sync_sessions:
            del sync_sessions[telegram_id]
        
        await callback.answer("✅ Диалог успешно синхронизирован!")
        await callback.message.edit_text(
            f"✅ Диалог синхронизирован!\n"
            f"Загружено сообщений: {len(messages)}\n\n"
            f"Теперь вы можете продолжить этот диалог."
        )
        
    except Exception as e:
        print(f"[ERROR] Ошибка при синхронизации диалога: {e}")
        await callback.answer("❌ Ошибка при синхронизации", show_alert=True)
        # Очищаем session при ошибке
        if telegram_id in sync_sessions:
            del sync_sessions[telegram_id]

