"""Утилиты для обработчиков"""

from .constants import LEGAL_KEYWORDS


def is_legal_query(text: str) -> bool:
    """Определяет, является ли запрос юридическим"""
    return any(word in text.lower() for word in LEGAL_KEYWORDS)


def get_system_prompt(is_legal: bool) -> str:
    """Возвращает системный промпт в зависимости от типа запроса"""
    if is_legal:
        return (
            "Ты юридический консультант для малого бизнеса. "
            "Объясняй законы и нормы простым языком."
        )
    else:
        return (
            "Ты эксперт по ведению малого бизнеса. "
            "Отвечай профессионально, структурированно и полезно."
        )

