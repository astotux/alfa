from aiogram import Router, F
from aiogram.types import Message, Document
import os
import logging
import asyncio
import re
from services.pdf_service import process_pdf_document, process_docx_document
from contextlib import suppress

router = Router()
logger = logging.getLogger(__name__)

TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)


class ProgressManager:
    """Менеджер для управления прогресс-баром"""

    def __init__(self, message: Message):
        self.message = message
        self.progress_msg = None
        self.last_progress = -1  # Инициализируем значением, которого никогда не будет

    async def update(self, text: str, progress: int):
        """Обновляет прогресс-бар, создавая или редактируя сообщение"""
        # Пропускаем обновление если прогресс не изменился
        if progress == self.last_progress:
            return

        self.last_progress = progress

        # Формируем сообщение с прогрессом
        progress_bar = self._create_progress_bar(progress)
        status_text = self._get_status_text(progress)

        message_text = (
            f"📊 **Анализ документа**\n\n"
            f"{text}\n\n"
            f"{progress_bar} {progress}%\n"
            f"{status_text}"
        )

        try:
            if self.progress_msg is None:
                # Создаем новое сообщение с прогрессом
                self.progress_msg = await self.message.answer(message_text, parse_mode="Markdown")
            else:
                # Редактируем существующее сообщение
                await self.progress_msg.edit_text(message_text, parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"Ошибка обновления прогресса: {str(e)}")
            # Если не удалось отредактировать - создаем новое сообщение
            try:
                if self.progress_msg:
                    await self.progress_msg.delete()
                self.progress_msg = await self.message.answer(message_text, parse_mode="Markdown")
            except Exception as e2:
                logger.error(f"Критическая ошибка управления прогрессом: {str(e2)}")

    def _create_progress_bar(self, progress: int) -> str:
        """Создает визуальный прогресс-бар"""
        filled = "🟢" * (progress // 10)
        empty = "⚪️" * (10 - progress // 10)
        return f"`[{filled}{empty}]`"

    def _get_status_text(self, progress: int) -> str:
        """Возвращает текстовый статус в зависимости от прогресса"""
        if progress <= 10:
            return "_Подготовка к анализу..._"
        elif progress <= 40:
            return "_Извлечение текста из документа..._"
        elif progress <= 85:
            return "_Анализ содержания документа ИИ..._"
        elif progress <= 95:
            return "_Формирование отчета..._"
        else:
            return "_Завершение обработки..._"

    async def finish(self):
        """Завершает прогресс-бар"""
        if self.progress_msg:
            try:
                # Редактируем сообщение на финальное состояние
                await self.progress_msg.edit_text(
                    "✅ **Анализ документа завершен!**\n\n"
                    "Отчет готов к просмотру ниже 👇",
                    parse_mode="Markdown"
                )
                # Автоматически удаляем через 3 секунды
                await asyncio.sleep(3)
                await self.progress_msg.delete()
            except Exception as e:
                logger.warning(f"Не удалось завершить прогресс-бар: {str(e)}")
                with suppress(Exception):
                    await self.progress_msg.delete()


@router.message(F.document)
async def handle_document(message: Message):
    """Обработчик документов (PDF и DOCX)"""
    document: Document = message.document
    progress_manager = ProgressManager(message)

    try:
        # Определение типа файла
        file_name = document.file_name or ""
        file_name_lower = file_name.lower()
        mime_type = document.mime_type or ""
        
        is_pdf = (
            mime_type == "application/pdf" or 
            file_name_lower.endswith('.pdf')
        )
        is_docx = (
            mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or
            file_name_lower.endswith('.docx')
        )
        
        if not is_pdf and not is_docx:
            # Проверяем, не старый ли это .doc файл
            if file_name_lower.endswith('.doc'):
                await message.answer(
                    "⚠️ **Неподдерживаемый формат**\n\n"
                    "Бот работает только с DOCX файлами (новый формат Word).\n"
                    "Старые .doc файлы не поддерживаются.\n\n"
                    "**Решение:**\n"
                    "1. Откройте .doc файл в Microsoft Word\n"
                    "2. Сохраните как .docx (Файл → Сохранить как → выберите .docx)\n"
                    "3. Отправьте новый файл",
                    parse_mode="Markdown"
                )
            else:
                await message.answer(
                    "⚠️ **Поддерживаемые форматы**\n\n"
                    "Бот работает с PDF и DOCX файлами. "
                    "Пожалуйста, отправьте документ с расширением .pdf или .docx",
                    parse_mode="Markdown"
                )
            return
        
        file_type = "PDF" if is_pdf else "DOCX"

        # Инициализация прогресса
        await progress_manager.update("Получение файла от Telegram", 5)

        # Генерация безопасного имени файла
        user_id = message.from_user.id
        original_filename = document.file_name or f"document.{'pdf' if is_pdf else 'docx'}"
        file_ext = "pdf" if is_pdf else "docx"
        safe_filename = f"{user_id}_{abs(hash(original_filename)) % 10000}.{file_ext}"
        input_path = os.path.join(TEMP_DIR, safe_filename)

        # Скачивание файла
        await progress_manager.update("Скачивание файла", 10)

        try:
            file = await message.bot.get_file(document.file_id)
            await message.bot.download_file(file.file_path, destination=input_path)

            if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
                raise ValueError("Файл не был сохранен или пустой")

            file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
            logger.info(f"Файл сохранен: {input_path}, размер: {file_size_mb:.2f}MB")

            if file_size_mb > 15:
                raise ValueError("Размер файла превышает 15MB")

        except Exception as e:
            logger.error(f"Ошибка скачивания файла: {str(e)}")
            raise ValueError("Не удалось скачать файл. Попробуйте отправить его еще раз.")

        # Получение инструкции от пользователя
        instruction = (message.caption or "").strip()

        if not instruction:
            instruction = "Проведите комплексную проверку оформления и содержания документа"
            await progress_manager.update("Анализ оформления документа", 25)
        else:
            short_instruction = instruction[:50] + "..." if len(instruction) > 50 else instruction
            await progress_manager.update(f"Запрос: {short_instruction}", 25)

        # Анализ документа
        if is_pdf:
            analysis_result = await process_pdf_document(
                input_path,
                instruction,
                lambda text, progress: progress_manager.update(text, progress)
            )
        else:
            analysis_result = await process_docx_document(
                input_path,
                instruction,
                lambda text, progress: progress_manager.update(text, progress)
            )

        # Отправка результата
        await progress_manager.finish()

        # Разбивка длинного текста на части
        await send_analysis_result(message, analysis_result)

    except ValueError as e:
        error_text = str(e)
        logger.warning(f"Ошибка обработки документа: {error_text}")
        await handle_processing_error(message, error_text, file_type if 'file_type' in locals() else "DOCUMENT")

    except Exception as e:
        logger.exception(f"Критическая ошибка обработки: {str(e)}")
        await message.answer(
            "🚨 **Критическая ошибка**\n\n"
            "Произошла непредвиденная ошибка при обработке документа.\n"
            "Пожалуйста, попробуйте отправить файл еще раз или обратитесь к поддержке.",
            parse_mode="Markdown"
        )

    finally:
        # Очистка временных файлов
        if 'input_path' in locals() and os.path.exists(input_path):
            try:
                os.remove(input_path)
                logger.info(f"Временный файл удален: {input_path}")
            except Exception as e:
                logger.warning(f"Ошибка удаления файла {input_path}: {str(e)}")

        # Убедимся, что прогресс-бар удален
        if 'progress_manager' in locals():
            with suppress(Exception):
                await progress_manager.finish()


async def send_analysis_result(message: Message, analysis: str):
    """Отправляет результат анализа, разбивая на части при необходимости"""
    max_length = 4000

    if len(analysis) <= max_length:
        await message.answer(
            f"📋 **Отчет по анализу документа**\n\n{analysis}",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return

    # Разбиваем на части по абзацам
    parts = []
    paragraphs = [p.strip() for p in analysis.split('\n\n') if p.strip()]

    current_part = "📋 **Отчет по анализу документа (часть 1)**\n\n"
    part_num = 1

    for paragraph in paragraphs:
        if len(current_part) + len(paragraph) + 2 > max_length:
            parts.append(current_part.strip())
            part_num += 1
            current_part = f"📋 **Продолжение отчета (часть {part_num})**\n\n{paragraph}\n\n"
        else:
            current_part += f"{paragraph}\n\n"

    if current_part.strip():
        parts.append(current_part.strip())

    # Отправляем части
    for i, part in enumerate(parts):
        if i > 0:
            await asyncio.sleep(1)  # Задержка между сообщениями

        await message.answer(
            part,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )


async def handle_processing_error(message: Message, error_text: str, file_type: str = "DOCUMENT"):
    """Обрабатывает ошибки обработки и отправляет пользователю понятное сообщение"""
    error_lower = error_text.lower()
    doc_type = "PDF" if "pdf" in file_type.lower() else "DOCX" if "docx" in file_type.lower() else "документ"

    if any(word in error_lower for word in ["паролем", "защищен", "encrypted", "protected"]):
        if "pdf" in doc_type.lower():
            response = (
                "🔒 Ошибка: защищенный PDF\n\n"
                "Документ защищен паролем. Для анализа необходимо снять защиту:\n"
                "1. Откройте PDF в Adobe Acrobat Reader\n"
                "2. Перейдите в меню «Файл» → «Свойства»\n"
                "3. На вкладке «Безопасность» выберите «Без защиты»\n"
                "4. Сохраните документ и отправьте повторно"
            )
        else:
            response = (
                "🔒 Ошибка: защищенный документ\n\n"
                "DOCX документ защищен паролем. Для анализа необходимо снять защиту:\n"
                "1. Откройте документ в Microsoft Word\n"
                "2. Перейдите в «Файл» → «Сведения» → «Защита документа»\n"
                "3. Снимите защиту документа\n"
                "4. Сохраните документ и отправьте повторно"
            )
    elif any(word in error_lower for word in ["скан", "изображени", "image", "ocr"]):
        response = (
            f"🖼️ Ошибка: сканированный документ\n\n"
            f"Бот анализирует только текстовые {doc_type} файлы. "
            "Для сканов необходимо выполнить OCR-распознавание:\n"
            "• После преобразования отправьте текстовую версию"
        )
    elif any(word in error_lower for word in ["поврежден", "corrupt", "damaged", "неверный формат"]):
        response = (
            f"❌ Ошибка: поврежденный файл\n\n"
            f"{doc_type} файл поврежден или имеет неверный формат.\n"
            "Проверьте целостность файла и попробуйте:\n"
            "1. Открыть файл в соответствующей программе\n"
            "2. Сохранить файл заново\n"
            "3. Отправить файл повторно"
        )
    elif any(word in error_lower for word in ["размер", "больш", "15mb", "мегабайт"]):
        response = (
            "📦 Ошибка: большой размер файла\n\n"
            "Максимальный размер файла — 15MB. "
            "Рекомендуется:\n"
            "1. Сжать PDF \n"
            "2. Разделить документ на части\n"
            "3. Отправить только ключевые страницы"
        )
    elif any(word in error_lower for word in ["таймаут", "timeout", "не ответил", "5 минут"]):
        response = (
            "⏱️ Ошибка: время ожидания истекло\n\n"
            "Анализ занял более 5 минут. Это может быть связано:\n"
            "• С большим объемом документа\n"
            "• Сложной структурой текста\n"
            "• Временной перегрузкой сервера\n\n"
            "Рекомендуется:\n"
            "1. Разделить документ на части\n"
            "2. Отправить только нужные разделы\n"
            "3. Повторить попытку через 5-10 минут"
        )
    else:
        response = (
            "❌ Ошибка обработки\n\n"
            f"{error_text.capitalize()}\n\n"
            f"Пожалуйста, проверьте корректность {doc_type} файла "
            "и попробуйте отправить его еще раз."
        )

    await message.answer(response, parse_mode="Markdown")