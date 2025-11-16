from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from services.llm_service import get_llm_response
from services.memory_service import memory
from services.db_service import db
from utils.disclaimers import LEGAL_DISCLAIMER
import re

router = Router()

# Session для хранения состояния пагинации чатов
# Структура: {telegram_id: {"chats": [...], "current_page": 0, "message_id": ...}}
sync_sessions = {}

# Session для хранения текущего chat_id пользователя
# Структура: {telegram_id: {"chat_id": "...", "user_id": "..."}}
user_chat_sessions = {}

CHATS_PER_PAGE = 5

# Клавиатура с кнопками
sync_button = KeyboardButton(text="📥 Синхронизировать диалог")
clear_button = KeyboardButton(text="🗑️ Очистить историю")
main_kb = ReplyKeyboardMarkup(
    keyboard=[[sync_button],[clear_button]],
    resize_keyboard=True,
    one_time_keyboard=False
)

LEGAL_KEYWORDS = ["закон", "юридический", "договор", "суд", "лицензия", "налог", "права", "юрист", "кодекс", "законодательство"]

@router.message(CommandStart())
async def handle_start(message: Message):
    """Обрабатывает /start и /start <токен>"""
    text = message.text or ""
    parts = text.split(maxsplit=1)
    token = parts[1] if len(parts) > 1 else None

    if token:
        try:
            # Ищем пользователя по токену
            user_id = await db.get_user_by_token(token)
            if user_id:
                telegram_id = message.from_user.id
                await db.update_telegram_id(user_id, telegram_id)
                await message.answer(
                    "Аккаунт успешно привязан к Telegram!\n\n"
                    "Теперь вы можете пользоваться всеми функциями ИИ-помощника.",
                    reply_markup=main_kb
                )
            else:
                await message.answer(
                    "Неверная или устаревшая ссылка синхронизации.\n"
                    "Пожалуйста, убедитесь, что вы перешли по корректной ссылке."
                )
        except Exception as e:
            print(f"[ERROR] Ошибка при синхронизации: {e}")
            await message.answer(
                "⚠Произошла ошибка при привязке аккаунта. Попробуйте позже."
            )
    else:
        # Обычный старт без токена
        await message.answer(
            "👋 Привет! Я ваш ИИ-помощник для микро-бизнеса.\n\n"
            "🔹 Генерирую тексты: документы, посты, письма\n"
            "🔹 Объясняю законы и нормы\n"
            "🔹 Отвечаю на любые бизнес-вопросы\n"
            "🔹 Редактирую PDF-документы\n\n"
            "Просто напишите запрос или отправьте PDF!",
            reply_markup=main_kb
        )

@router.message(F.text == "🗑️ Очистить историю")
async def clear_history(message: Message):
    telegram_id = message.from_user.id
    memory.clear(telegram_id)
    
    # Очищаем текущий chat_id из session (будет создан новый при следующем сообщении)
    if telegram_id in user_chat_sessions:
        del user_chat_sessions[telegram_id]
    
    await message.answer("✅ История диалога успешно очищена!", reply_markup=main_kb)

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

@router.message(F.text == "📥 Синхронизировать диалог")
async def sync_dialog(message: Message):
    """Показывает список диалогов для синхронизации с пагинацией"""
    telegram_id = message.from_user.id
    
    try:
        # Получаем user_id по telegram_id
        user_id = await db.get_user_id_by_telegram_id(telegram_id)
        
        if not user_id:
            await message.answer(
                "⚠️ Ваш аккаунт не привязан к системе.\n"
                "Привяжите аккаунт через наш сайт!",
                reply_markup=main_kb
            )
            return
        
        # Получаем список чатов пользователя
        chats = await db.get_user_chats(user_id)
        
        if not chats:
            await message.answer(
                "📭 У вас пока нет сохранённых диалогов в системе.",
                reply_markup=main_kb
            )
            return
        
        # Сохраняем чаты в session
        reply_markup = build_chats_keyboard(chats, 0)
        
        sent_message = await message.answer(
            "📋 Выберите диалог для синхронизации:",
            reply_markup=reply_markup
        )
        
        # Сохраняем состояние в session
        sync_sessions[telegram_id] = {
            "chats": chats,
            "current_page": 0,
            "message_id": sent_message.message_id
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Ошибка при получении диалогов: {e}")
        print(f"[ERROR] Детали: {error_details}")
        await message.answer(
            f"❌ Не удалось загрузить список диалогов.\n\nОшибка: {str(e)}\n\nПопробуйте позже.",
            reply_markup=main_kb
        )

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

@router.message(F.text)
async def handle_message(message: Message):
    user_query = message.text.strip()

    # Игнорируем кнопки (на случай дублирования)
    if user_query in ["🗑️ Очистить историю", "📥 Синхронизировать диалог"]:
        return

    telegram_id = message.from_user.id
    
    # Пытаемся получить user_id из БД (может быть None, если пользователь не авторизован)
    user_id = None
    try:
        user_id = await db.get_user_id_by_telegram_id(telegram_id)
    except Exception as e:
        print(f"[ERROR] Ошибка при получении user_id: {e}")
        # Продолжаем работу без сохранения в БД

    # Получаем или создаем chat_id (только для авторизованных пользователей)
    chat_id = None
    if user_id:
        # Пользователь авторизован - работаем с БД
        if telegram_id in user_chat_sessions:
            chat_id = user_chat_sessions[telegram_id].get("chat_id")
        
        # Если нет активного чата, создаем новый
        if not chat_id:
            try:
                # Используем первые 100 символов запроса как заголовок
                title = user_query[:100] if len(user_query) > 0 else "Новый диалог"
                chat_id = await db.create_chat(user_id, title)
                
                # Сохраняем в session
                if telegram_id not in user_chat_sessions:
                    user_chat_sessions[telegram_id] = {}
                user_chat_sessions[telegram_id]["chat_id"] = chat_id
                user_chat_sessions[telegram_id]["user_id"] = user_id
            except Exception as e:
                print(f"[ERROR] Ошибка при создании чата: {e}")
                # Продолжаем работу без сохранения в БД

        # Сохраняем сообщение пользователя в БД
        if chat_id:
            try:
                await db.create_message(chat_id, "user", user_query)
            except Exception as e:
                print(f"[ERROR] Ошибка при сохранении сообщения пользователя: {e}")

    # Работаем с памятью (для всех пользователей - авторизованных и неавторизованных)
    context = memory.get_summary(telegram_id)

    # Определяем, юридический ли запрос
    is_legal_query = any(word in user_query.lower() for word in LEGAL_KEYWORDS)

    if is_legal_query:
        system_prompt = (
            "Ты юридический консультант для малого бизнеса. Объясняй законы и нормы простым языком. "
            ""
        )
    else:
        system_prompt = (
            "Ты эксперт по ведению малого бизнеса. Отвечай профессионально, структурированно и полезно."
        )

    try:
        full_response = await get_llm_response(
            query=user_query,
            context=context,
            system_prompt=system_prompt
        )
    except Exception as e:
        print(f"[ERROR] LLM error: {e}")
        await message.answer("❌ Не удалось получить ответ. Попробуйте позже.")
        return

    # Добавляем дисклеймер для юридических вопросов
    if is_legal_query and LEGAL_DISCLAIMER not in full_response:
        response = f"{full_response}\n\n{LEGAL_DISCLAIMER}"
    else:
        response = full_response

    # Сохраняем сообщение ассистента в БД (только для авторизованных пользователей)
    if chat_id and user_id:
        try:
            await db.create_message(chat_id, "assistant", response)
        except Exception as e:
            print(f"[ERROR] Ошибка при сохранении сообщения ассистента: {e}")

    # Сохраняем в память (для всех пользователей)
    memory.add_message(telegram_id, f"Пользователь: {user_query}\nАссистент: {response}")

    # Отправляем ответ частями (ограничение Telegram — 4096 символов)
    for i in range(0, len(response), 4000):
        await message.answer(response[i:i + 4000], reply_markup=main_kb)