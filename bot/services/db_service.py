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

# === ВАЖНО: создаём глобальный экземпляр ===
db = DBService(DATABASE_PATH)