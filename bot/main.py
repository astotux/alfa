import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()


from aiogram import Bot, Dispatcher
from handlers import document_handler, message_handler


async def main():
    logging.basicConfig(level=logging.INFO)

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("❌ TELEGRAM_TOKEN не найден в .env файле!")

    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_router(message_handler.router)
    dp.include_router(document_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())