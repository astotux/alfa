from pydantic import BaseModel
from typing import Optional

class CreateChat(BaseModel):
    question: str
    chat_type: Optional[str] = "general"
    
class CreateMessage(BaseModel):
    chatId: str
    content: str
    role: str