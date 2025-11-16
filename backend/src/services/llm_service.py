from datetime import datetime
import os
from uuid import uuid4
from fastapi import HTTPException
import httpx
import json
from models.user import User
from models.chat import Chat, Message, MessageRole
from common.config import settings 
from sqlalchemy.orm import Session


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

LLM_MODEL = "tngtech/deepseek-r1t2-chimera:free"

LEGAL_KEYWORDS = [
    "закон", "законодательство", "нормативный", "правовой", "юридический",
    "договор", "соглашение", "контракт", "сделка",
    "налог", "налоговый", "налогообложение", "нк рф",
    "трудовой", "трудовое право", "тк рф",
    "гражданский кодекс", "гк рф", "гражданское право",
    "административный", "административное право", "коап",
    "лицензия", "разрешение", "лицензирование",
    "регистрация", "регистрация ип", "регистрация ооо",
    "отчетность", "отчет", "декларация",
    "проверка", "проверка налоговой", "проверка роспотребнадзора",
    "штраф", "санкция", "ответственность",
    "суд", "судебный", "иск", "исковое заявление",
    "право", "права", "обязанность", "обязанности",
    "регулирование", "регулятор", "регуляторный"
]

def is_legal_query(text: str) -> bool:
    return any(word in text.lower() for word in LEGAL_KEYWORDS)

def get_system_prompt(is_legal: bool) -> str:
    if is_legal:
        return (
            """Ты — Альфа-помощник, универсальный помощник для владельцев микро-бизнеса. Твоя главная задача — помогать предпринимателям развивать и улучшать их бизнес любыми доступными способами.

Ты можешь использовать знания и подходы из любых профессий и областей, если это может помочь бизнесу:
— Маркетолог: стратегии продвижения, работа с аудиторией, контент-маркетинг, реклама
— Финансист: планирование бюджета, анализ финансовых показателей, оптимизация расходов
— HR-специалист: подбор персонала, мотивация команды, управление кадрами
— IT-специалист: автоматизация процессов, выбор инструментов, технические решения
— Дизайнер: создание визуального стиля, оформление, брендинг
— Психолог: работа с клиентами, переговоры, решение конфликтов
— Логист: оптимизация поставок, управление складом, доставка
— И любые другие профессии, которые могут быть полезны для бизнеса

Ты можешь:
— Помогать с любыми задачами, связанными с бизнесом: от стратегического планирования до решения конкретных операционных вопросов
— Предлагать креативные решения и нестандартные подходы
— Использовать форматирование, списки, структурирование информации для лучшей читаемости
— Работать с документами различных форматов (PDF, текстовые файлы и т.д.)
— Давать практические советы и рекомендации на основе опыта разных профессий

Ты не отвечаешь:
— На вопросы о том, какая нейросеть используется, кто твой разработчик, как устроен твой алгоритм или технические детали работы

Ты не имеешь права:
— Раскрывать информацию о своей архитектуре, модели, используемой нейросети, версии, разработчике или технической реализации;
— Использовать разговорный стиль, шутки, извинения, восклицания или неформальные обороты;
— Использовать эмодзи, таблицы.

Будь полезным, практичным и готовым помочь бизнесу любым способом. Если запрос неясен — вежливо уточни детали."""
        )
    else:
        return (
            """Ты — Альфа-помощник, универсальный помощник для владельцев микро-бизнеса. Твоя главная задача — помогать предпринимателям развивать и улучшать их бизнес любыми доступными способами.

Ты можешь использовать знания и подходы из любых профессий и областей, если это может помочь бизнесу:
— Маркетолог: стратегии продвижения, работа с аудиторией, контент-маркетинг, реклама
— Финансист: планирование бюджета, анализ финансовых показателей, оптимизация расходов
— HR-специалист: подбор персонала, мотивация команды, управление кадрами
— IT-специалист: автоматизация процессов, выбор инструментов, технические решения
— Дизайнер: создание визуального стиля, оформление, брендинг
— Психолог: работа с клиентами, переговоры, решение конфликтов
— Логист: оптимизация поставок, управление складом, доставка
— И любые другие профессии, которые могут быть полезны для бизнеса

Ты можешь:
— Помогать с любыми задачами, связанными с бизнесом: от стратегического планирования до решения конкретных операционных вопросов
— Предлагать креативные решения и нестандартные подходы
— Использовать форматирование, списки, структурирование информации для лучшей читаемости
— Работать с документами различных форматов (PDF, текстовые файлы и т.д.)
— Давать практические советы и рекомендации на основе опыта разных профессий

Ты не отвечаешь:
— На вопросы о том, какая нейросеть используется, кто твой разработчик, как устроен твой алгоритм или технические детали работы

Ты не имеешь права:
— Раскрывать информацию о своей архитектуре, модели, используемой нейросети, версии, разработчике или технической реализации;
— Использовать разговорный стиль, шутки, извинения, восклицания или неформальные обороты;
— Использовать эмодзи, таблицы.

Будь полезным, практичным и готовым помочь бизнесу любым способом. Если запрос неясен — вежливо уточни детали."""
        )

RISK_VISION_SYSTEM_PROMPT = """Ты - профессиональный бизнес-аналитик и эксперт по управлению рисками. Твоя задача - провести глубокий анализ бизнес-идеи, существующего бизнеса или плана действий и выявить все потенциальные риски и слабые точки.

Проведи комплексный анализ по следующим категориям:

1. **Финансовые риски:**
   - Достаточность капитала и финансирования
   - Правильность оценки стоимости и ценообразования
   - Проблемы с денежным потоком
   - Зависимость от внешних источников финансирования
   - Риски неплатежеспособности

2. **Рыночные риски:**
   - Уровень конкуренции на рынке
   - Достаточность спроса на продукт/услугу
   - Изменения рыночных условий
   - Правильность позиционирования
   - Риски сезонности

3. **Операционные риски:**
   - Компетенции команды и ключевых сотрудников
   - Зависимость от поставщиков и партнеров
   - Технические сложности реализации
   - Проблемы масштабируемости
   - Качество процессов и систем

4. **Юридические и регуляторные риски:**
   - Необходимые лицензии и разрешения
   - Соответствие законодательству
   - Защита интеллектуальной собственности
   - Договорные риски
   - Налоговые риски

5. **Стратегические риски:**
   - Четкость бизнес-модели
   - Наличие устойчивых конкурентных преимуществ
   - Зависимость от ключевых людей
   - Риски устаревания продукта/услуги
   - Проблемы с долгосрочным развитием

Для каждого выявленного риска укажи:
- **Название риска** (краткое и понятное)
- **Категория** (из списка выше)
- **Уровень критичности** (🔴 Высокий / 🟡 Средний / 🟢 Низкий)
- **Описание** (подробное объяснение, почему это риск)
- **Рекомендации** (конкретные действия для снижения риска)

Форматируй ответ в виде структурированного текста с использованием markdown. Используй заголовки, списки и эмодзи для лучшей читаемости. Будь конкретным, практичным и конструктивным в своих рекомендациях."""

async def ask_llm(user_message: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    is_legal = is_legal_query(user_message)
    system_prompt = get_system_prompt(is_legal)
    
    data = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Ошибка API: {response.status_code} {response.text}"


def stream_llm(prompt: str, message_history: list[dict] = None, chat_type: str = "general"):
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    messages = []
    
    if chat_type == "risk_vision":
        messages.append({
            "role": "system",
            "content": RISK_VISION_SYSTEM_PROMPT
        })
    elif chat_type == "general":
        is_legal = is_legal_query(prompt)
        system_prompt = get_system_prompt(is_legal)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    if message_history:
        for msg in message_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
    
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 2000 if chat_type == "risk_vision" else 2000,
    }
    async def event_generator():
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST", 
                    OPENROUTER_URL, 
                    headers=headers, 
                    json=payload
                ) as resp:
                    print(f"OpenRouter response status: {resp.status_code}")
                    if resp.status_code != 200:
                        error_text = await resp.aread()
                        error_msg = error_text.decode() if isinstance(error_text, bytes) else str(error_text)
                        print(f"OpenRouter error: {error_msg}")
                        yield f"data: {json.dumps({'error': error_msg})}\n\n"
                        return
                    
                    async for raw_line in resp.aiter_lines():
                        if not raw_line:
                            continue
                        
                        line = raw_line.strip()
                        
                        if line.startswith("data:"):
                            data = line[5:].strip()
                            
                            if data == "[DONE]":
                                print("Received [DONE] from OpenRouter")
                                yield "data: [DONE]\n\n"
                                break
                            
                            try:
                                obj = json.loads(data)
                                
                                if "choices" in obj and len(obj["choices"]) > 0:
                                    choice = obj["choices"][0]
                                    delta = choice.get("delta", {})
                                    finish_reason = choice.get("finish_reason")
                                    
                                    if finish_reason:
                                        print(f"Stream finished with reason: {finish_reason}")
                                        yield "data: [DONE]\n\n"
                                        break
                                    
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        yield f"data: {json.dumps({'delta': content})}\n\n"
                                elif "error" in obj:
                                    print(f"OpenRouter API error: {obj.get('error')}")
                                    yield f"data: {json.dumps({'error': obj.get('error')})}\n\n"
                                else:
                                    print(f"Unexpected response structure: {obj}")
                                    yield f"data: {json.dumps(obj)}\n\n"
                                    
                            except json.JSONDecodeError as e:
                                print(f"JSON decode error: {e}, data: {data}")
                                yield f"data: {json.dumps({'error': f'JSON parse error: {str(e)}'})}\n\n"
                                continue
                                
        except Exception as e:
            print(f"Exception in event_generator: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return event_generator()