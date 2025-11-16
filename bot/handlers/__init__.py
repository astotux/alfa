"""Обработчики для Telegram бота"""

from .start_handler import router as start_router
from .button_handlers import router as button_router
from .callback_handlers import router as callback_router
from .chat_handler import router as chat_router
from .document_handler import router as document_router

__all__ = [
    "start_router",
    "button_router",
    "callback_router",
    "chat_router",
    "document_router",
]

