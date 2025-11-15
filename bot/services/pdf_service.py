import fitz  # PyMuPDF
from services.llm_service import get_llm_response
import logging

logger = logging.getLogger(__name__)

async def extract_text_from_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        text = ""
        for page_num, page in enumerate(doc):
            text += page.get_text()
            if len(text) > 50000:  # Ограничение, чтобы не уйти в бесконечность
                logger.warning(f"PDF слишком большой (страница {page_num}). Обрезаем текст.")
                break
        doc.close()
        return text[:50000]  # Ограничение на 50k символов
    except Exception as e:
        logger.exception("Ошибка при извлечении текста из PDF")
        raise ValueError("Не удалось прочитать PDF. Возможно, он зашифрован или повреждён.")

async def process_pdf_document(input_path: str, instruction: str) -> str:
    try:
        # 1. Извлечение текста
        original_text = await extract_text_from_pdf(input_path)
        if not original_text.strip():
            raise ValueError("PDF не содержит текста (возможно, это скан-изображение).")

        # 2. Формирование промпта
        prompt = f"""
Инструкция: {instruction}

Исходный текст документа:
{original_text}

Твоя задача:
- Перепиши документ в соответствии с инструкцией.
- Сохрани деловой стиль и логическую структуру.
- Не выдумывай факты.
- Верни ТОЛЬКО текст нового документа без пояснений.
"""

        # 3. Запрос к LLM
        processed_text = await get_llm_response(
            query=prompt,
            context="",
            system_prompt="Ты профессиональный редактор бизнес-документов. Возвращай ТОЛЬКО исправленный текст."
        )

        # 4. Создание нового PDF
        output_path = input_path.replace(".pdf", "_edited.pdf")
        doc = fitz.open()
        page = doc.new_page()

        # Добавляем текст с переносами (ограничение: fitz не делает авто-ворд-врап)
        # Для простоты — вставляем как есть (в реальном проекте можно использовать более сложную вёрстку)
        page.insert_text(
            point=(50, 50),
            text=processed_text[:10000],  # Ограничение для демонстрации
            fontsize=11,
            width=500  # ширина "колонки" в пунктах
        )
        doc.save(output_path)
        doc.close()

        return output_path

    except Exception as e:
        logger.exception("Ошибка в process_pdf_document")
        raise