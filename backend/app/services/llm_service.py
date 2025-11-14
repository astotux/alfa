import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def ask_llm(user_message: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
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
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "max_tokens": 400,
    }

    async def event_generator():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", OPENROUTER_URL, headers=headers, json=payload) as resp:
                async for raw_line in resp.aiter_lines():
                    if not raw_line:
                        continue
                    line = raw_line.strip()
                    if line.startswith("data:"):
                        data = line[len("data:"):].strip()
                        if data == "[DONE]":
                            yield "event: done\ndata: [DONE]\n\n"
                            break
                        try:
                            obj = json.loads(data)
                        except Exception:
                            yield f"data: {json.dumps({'raw': data})}\n\n"
                            continue
                        if obj.get("type") == "response.content_part.delta":
                            delta = obj.get("delta") or obj.get("part", {}).get("text")
                            if delta is None:
                                yield f"data: {json.dumps(obj)}\n\n"
                            else:
                                yield f"data: {json.dumps({'delta': delta})}\n\n"
                        else:
                            yield f"data: {json.dumps(obj)}\n\n"

    return event_generator()
