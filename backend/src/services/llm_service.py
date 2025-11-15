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


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def ask_llm(user_message: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [{"role": "user", "content": user_message}]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Ошибка API: {response.status_code} {response.text}"


def stream_llm(chat_id: str, user_message: str, db: Session, user: User):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat or chat.userId != user.id:
        raise HTTPException(status_code=404, detail="Чат не найден или нет доступа")


    user_msg = Message(
        id=str(uuid4()),
        chatId=chat.id,
        role=MessageRole.user,
        content=user_message,
        createdAt=datetime.now()
    )
    db.add(user_msg)
    chat.updatedAt = datetime.now()
    db.commit()
    db.refresh(user_msg)


    async def event_generator():
        ai_content = ""  

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "messages": [{"role": "user", "content": user_message}],
            "stream": True,
            "max_tokens": 400,
        }

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", OPENROUTER_URL, headers=headers, json=payload) as resp:
                async for raw_line in resp.aiter_lines():
                    if not raw_line:
                        continue
                    line = raw_line.strip()
                    if line.startswith("data:"):
                        data = line[len("data:"):].strip()
                        if data == "[DONE]":
                            break
                        try:
                            obj = json.loads(data)
                        except Exception:
                            continue
                        if obj.get("type") == "response.content_part.delta":
                            delta = obj.get("delta") or obj.get("part", {}).get("text")
                            if delta:
                                ai_content += delta
                                yield f"data: {json.dumps({'delta': delta})}\n\n"

        ai_msg = Message(
            id=str(uuid4()),
            chatId=chat.id,
            role=MessageRole.assistant,
            content=ai_content,
            createdAt=datetime.utcnow()
        )
        db.add(ai_msg)
        db.commit()
        yield "event: done\ndata: [DONE]\n\n"

    return event_generator()
