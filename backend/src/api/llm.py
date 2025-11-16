from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.llm_service import ask_llm, stream_llm
from database.database import get_db
from models.chat import Chat, Message as ChatMessage, ChatType
from auth.dependencies import get_current_user
from models.user import User


router = APIRouter()

class Message(BaseModel):
    message: str

@router.get("/api/stream")
async def stream_get(
    prompt: str,
    chat_id: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    message_history = []
    
    if chat_id:
        chat = (
            db.query(Chat)
            .filter(Chat.id == chat_id, Chat.userId == user.id)
            .first()
        )
        
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.chatId == chat_id)
            .order_by(ChatMessage.createdAt.asc())
            .all()
        )
        
        for msg in messages:
            message_history.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        chat_type = chat.chatType.value if chat.chatType else "general"
    else:
        chat_type = "general"
    
    event_generator = stream_llm(prompt, message_history, chat_type)
    return StreamingResponse(
        event_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/api/chat")
async def chat_endpoint(msg: Message):
    response_text = await ask_llm(msg.message)
    return {"reply": response_text}