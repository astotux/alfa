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


def stream_llm(prompt: str):
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "max_tokens": 400,
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
                    if resp.status_code != 200:
                        error_text = await resp.aread()
                        yield f"data: {json.dumps({'error': error_text.decode()})}\n\n"
                        return
                    
                    async for raw_line in resp.aiter_lines():
                        if not raw_line:
                            continue
                        
                        line = raw_line.strip()
                        
                        if line.startswith("data:"):
                            data = line[5:].strip()  # Убираем "data:" префикс
                            
                            if data == "[DONE]":
                                yield "data: [DONE]\n\n"
                                break
                            
                            try:
                                obj = json.loads(data)
                                
                                # OpenRouter использует формат OpenAI
                                if "choices" in obj:
                                    delta = obj["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        yield f"data: {json.dumps({'delta': content})}\n\n"
                                else:
                                    # Если другая структура - отправляем как есть
                                    yield f"data: {json.dumps(obj)}\n\n"
                                    
                            except json.JSONDecodeError as e:
                                yield f"data: {json.dumps({'error': f'JSON parse error: {str(e)}'})}\n\n"
                                continue
                                
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return event_generator()