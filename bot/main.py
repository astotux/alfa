import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from dotenv import load_dotenv
import requests

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/test")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_command(message: Message):
    await message.reply("Привет! Я ваш бизнес-ассистент.")

@dp.message_handler()
async def echo(message: Message):
    # Отправляем текст на Backend
    response = requests.get(API_URL)
    data = response.json()
    await message.reply(f"Ответ Backend: {data['message']}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
