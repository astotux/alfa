from aiogram import Router, F
from aiogram.types import Message, Document
import os
import logging
from services.pdf_service import process_pdf_document

router = Router()
logger = logging.getLogger(__name__)

TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)


@router.message(F.document)
async def handle_document(message: Message):
    document: Document = message.document

    # Проверка: это PDF?
    if document.mime_type != "application/pdf" and not (document.file_name and document.file_name.lower().endswith('.pdf')):
        await message.answer("⚠️ Я поддерживаю только PDF-файлы. Пожалуйста, отправьте документ с расширением .pdf")
        return

    # Генерация безопасного имени файла
    user_id = message.from_user.id
    original_filename = document.file_name or "document.pdf"
    safe_filename = f"{user_id}_{hash(original_filename) % 10000}.pdf"
    input_path = os.path.join(TEMP_DIR, safe_filename)
    output_path = None

    try:
        # Уведомляем пользователя, что началась обработка
        await message.answer("⏳ Обрабатываю ваш PDF-документ... Это может занять до 30 секунд.")

        # Скачиваем файл
        bot_file = await message.bot.get_file(document.file_id)
        await message.bot.download_file(bot_file.file_path, destination=input_path)
        logger.info(f"Файл сохранён: {input_path}")

        # Получаем инструкцию (если пользователь написал текст вместе с документом — но в Telegram это невозможно)
        # Поэтому просим уточнить задачу, если текст не передан
        instruction = message.caption or message.text or "Улучши документ, сохранив структуру и деловой стиль."

        # Обрабатываем PDF
        output_path = await process_pdf_document(input_path, instruction)

        # Отправляем результат
        await message.answer_document(
            document=output_path,
            caption="✅ Ваш обработанный PDF-документ готов!"
        )

    except Exception as e:
        logger.exception("Ошибка при обработке PDF")
        await message.answer(
            "❌ Произошла ошибка при обработке PDF.\n"
            "Пожалуйста, убедитесь, что файл не повреждён и не защищён паролем."
        )

    finally:
        # Очистка временных файлов
        for path in [input_path, output_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"Удалён временный файл: {path}")
                except Exception as e:
                    logger.warning(f"Не удалось удалить файл {path}: {e}")