import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Получаем путь к БД из .env
DATABASE_PATH = os.getenv("DATABASE_PATH", "DATABASE_PATH")

from aiogram import Bot, Dispatcher
from handlers import (
    start_router,
    button_router,
    callback_router,
    chat_router,
    document_router
)

# Создаём экземпляр DBService с указанием пути
from services.db_service import DBService
db = DBService(DATABASE_PATH)

async def main():
    # ⚠️ НЕ вызываем init_db() — таблицы уже существуют!

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("❌ TELEGRAM_TOKEN не найден в .env!")

    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(button_router)
    dp.include_router(callback_router)
    dp.include_router(chat_router)
    dp.include_router(document_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())