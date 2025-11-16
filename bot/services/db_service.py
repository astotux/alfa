import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH")

class DBService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def get_user_by_token(self, token: str):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM sync_tokens WHERE token = ?",
                (token,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None

    async def update_telegram_id(self, user_id: str, telegram_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET telegram_id = ? WHERE id = ?",
                (telegram_id, user_id)
            )
            await db.commit()

    async def get_user_id_by_telegram_id(self, telegram_id: int):
        """Получает user_id по telegram_id"""
        if not self.db_path:
            raise ValueError("Путь к базе данных не установлен")
        
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "SELECT id FROM users WHERE telegram_id = ?",
                (telegram_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None

    async def get_user_chats(self, user_id: str):
        """Получает список чатов пользователя"""
        if not self.db_path:
            raise ValueError("Путь к базе данных не установлен")
        
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("PRAGMA foreign_keys = ON")
            cursor = await conn.execute(
                "SELECT id, title, updatedAt FROM chats WHERE userId = ? ORDER BY updatedAt DESC",
                (user_id,)
            )
            rows = await cursor.fetchall()
            return [
                {"id": row[0], "title": row[1] or "Без названия", "updatedAt": row[2]}
                for row in rows
            ]

    async def get_chat_messages(self, chat_id: str):
        """Получает все сообщения из чата"""
        if not self.db_path:
            raise ValueError("Путь к базе данных не установлен")
        
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "SELECT role, content FROM messages WHERE chatId = ? ORDER BY createdAt ASC",
                (chat_id,)
            )
            rows = await cursor.fetchall()
            return [
                {"role": row[0], "content": row[1]}
                for row in rows
            ]

# === ВАЖНО: создаём глобальный экземпляр ===
db = DBService(DATABASE_PATH)