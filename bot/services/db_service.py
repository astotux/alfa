import aiosqlite
import os
from pathlib import Path
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime

load_dotenv()

# Получаем путь к базе данных из .env или используем относительный путь
DATABASE_PATH_ENV = os.getenv("DATABASE_PATH")

if DATABASE_PATH_ENV:
    # Если путь указан в .env, используем его
    if os.path.isabs(DATABASE_PATH_ENV):
        # Абсолютный путь
        DATABASE_PATH = DATABASE_PATH_ENV
    else:
        # Относительный путь - вычисляем относительно папки бота
        bot_dir = Path(__file__).parent.parent  # Переходим из services/ в bot/
        DATABASE_PATH = str(bot_dir / DATABASE_PATH_ENV)
else:
    # Если не указан в .env, используем путь по умолчанию
    bot_dir = Path(__file__).parent.parent  # Переходим из services/ в bot/
    DATABASE_PATH = str(bot_dir / ".." / "backend" / "llm.db")

# Преобразуем путь в абсолютный и нормализуем
DATABASE_PATH = str(Path(DATABASE_PATH).resolve())

class DBService:
    def __init__(self, db_path: str):
        # Если передан относительный путь или это не реальный путь, вычисляем относительно папки бота
        if db_path == "DATABASE_PATH" or not os.path.isabs(db_path):
            # Вычисляем путь относительно папки бота
            bot_dir = Path(__file__).parent.parent  # Переходим из services/ в bot/
            if db_path == "DATABASE_PATH":
                # Используем путь по умолчанию
                self.db_path = str((bot_dir / ".." / "backend" / "llm.db").resolve())
            else:
                self.db_path = str(Path(bot_dir / db_path).resolve())
        else:
            self.db_path = str(Path(db_path).resolve())
        
        # Проверяем существование файла
        if not os.path.exists(self.db_path):
            print(f"[WARNING] База данных не найдена по пути: {self.db_path}")
            print(f"[WARNING] Текущая рабочая директория: {os.getcwd()}")
            print(f"[WARNING] Попытка использовать путь по умолчанию...")
            # Пробуем путь по умолчанию
            bot_dir = Path(__file__).parent.parent
            default_path = str((bot_dir / ".." / "backend" / "llm.db").resolve())
            if os.path.exists(default_path):
                self.db_path = default_path
                print(f"[INFO] Использован путь по умолчанию: {self.db_path}")
            else:
                raise FileNotFoundError(f"❌ База данных не найдена по пути: {self.db_path}\nПроверенный путь по умолчанию: {default_path}")
        
        print(f"[INFO] DBService инициализирован с путем: {self.db_path}")

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

    async def create_chat(self, user_id: str, title: str = None) -> str:
        """Создает новый чат и возвращает его ID"""
        if not self.db_path:
            raise ValueError("Путь к базе данных не установлен")
        
        chat_id = str(uuid4())
        now = datetime.now()
        
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "INSERT INTO chats (id, title, userId, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?)",
                (chat_id, title, user_id, now, now)
            )
            await conn.commit()
        
        return chat_id

    async def create_message(self, chat_id: str, role: str, content: str) -> str:
        """Создает новое сообщение в чате и возвращает его ID"""
        if not self.db_path:
            raise ValueError("Путь к базе данных не установлен")
        
        message_id = str(uuid4())
        now = datetime.now()
        
        async with aiosqlite.connect(self.db_path) as conn:
            # Создаем сообщение
            await conn.execute(
                "INSERT INTO messages (id, chatId, role, content, createdAt) VALUES (?, ?, ?, ?, ?)",
                (message_id, chat_id, role, content, now)
            )
            # Обновляем updatedAt чата
            await conn.execute(
                "UPDATE chats SET updatedAt = ? WHERE id = ?",
                (now, chat_id)
            )
            await conn.commit()
        
        return message_id

    async def get_current_chat_id(self, user_id: str) -> str:
        """Получает ID последнего активного чата пользователя"""
        if not self.db_path:
            raise ValueError("Путь к базе данных не установлен")
        
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "SELECT id FROM chats WHERE userId = ? ORDER BY updatedAt DESC LIMIT 1",
                (user_id,)
            )
            row = await cursor.fetchone()
            return row[0] if row else None

# === ВАЖНО: создаём глобальный экземпляр ===
print(f"[INFO] Создание глобального экземпляра DBService с DATABASE_PATH: {DATABASE_PATH}")
db = DBService(DATABASE_PATH)