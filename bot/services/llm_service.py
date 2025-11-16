from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


async def get_llm_response(query: str, context: str, system_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Контекст предыдущих сообщений:\n{context}\n\nТекущий запрос:\n{query}"}
    ]

    response = await client.chat.completions.create(
        model="tngtech/deepseek-r1t2-chimera:free",
        messages=messages,
        temperature=0.7,
        max_tokens=2000
    )
    #model="deepseek/deepseek-chat-v3.1:free
    #meta-llama/llama-3.2-3b-instruct:free
    #qwen/qwen3-14b:free
    #tngtech/deepseek-r1t2-chimera:free
    return response.choices[0].message.content