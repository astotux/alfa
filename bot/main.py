import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Получаем путь к БД из .env
DATABASE_PATH = os.getenv("DATABASE_PATH", "DATABASE_PATH")

from aiogram import Bot, Dispatcher
from handlers import document_handler, message_handler

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

    dp.include_router(message_handler.router)
    dp.include_router(document_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())