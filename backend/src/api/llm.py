from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.llm_service import ask_llm, stream_llm


router = APIRouter()

class Message(BaseModel):
    message: str

@router.get("/api/stream")
async def stream_get(prompt: str):
    event_generator = stream_llm(prompt)
    return StreamingResponse(event_generator, media_type="text/event-stream")


@router.post("/api/chat")
async def chat_endpoint(msg: Message):
    response_text = await ask_llm(msg.message)
    return {"reply": response_text}