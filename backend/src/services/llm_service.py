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


def stream_llm(prompt: str, message_history: list[dict] = None):
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    messages = []
    if message_history:
        for msg in message_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
    
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": messages,
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