"""Клавиатуры для бота"""

from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from .constants import CHATS_PER_PAGE


# Основная клавиатура с кнопками
sync_button = KeyboardButton(text="📥 Синхронизировать диалог")
clear_button = KeyboardButton(text="🗑️ Очистить историю")
main_kb = ReplyKeyboardMarkup(
    keyboard=[[sync_button], [clear_button]],
    resize_keyboard=True,
    one_time_keyboard=False
)


def build_chats_keyboard(chats: list, page: int) -> InlineKeyboardMarkup:
    """Строит клавиатуру с чатами для указанной страницы"""
    total_pages = (len(chats) + CHATS_PER_PAGE - 1) // CHATS_PER_PAGE
    start_idx = page * CHATS_PER_PAGE
    end_idx = min(start_idx + CHATS_PER_PAGE, len(chats))
    
    keyboard = []
    
    # Добавляем кнопки с чатами для текущей страницы
    for chat in chats[start_idx:end_idx]:
        title = chat["title"][:50]  # Ограничиваем длину названия
        keyboard.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"sync_chat_{chat['id']}"
            )
        ])
    
    # Добавляем кнопки навигации в один ряд
    if total_pages > 1:
        nav_buttons = []
        
        # Кнопка "Назад" слева
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"sync_page_{page - 1}"
            ))
        
        # Кнопка с номером страницы по середине
        nav_buttons.append(InlineKeyboardButton(
            text=f"📄 {page + 1}/{total_pages}",
            callback_data="sync_page_info"
        ))
        
        # Кнопка "Вперед" справа
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton(
                text="Вперед ▶️",
                callback_data=f"sync_page_{page + 1}"
            ))
        
        keyboard.append(nav_buttons)
    
    # Кнопка "Начать новый диалог" снизу в отдельной строке
    keyboard.append([
        InlineKeyboardButton(
            text="🆕 Начать новый диалог",
            callback_data="start_new_chat"
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return reply_markup

