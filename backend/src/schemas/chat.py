from pydantic import BaseModel

class CreateChat(BaseModel):
    question: str
    
class CreateMessage(BaseModel):
    chatId: str
    content: str
    role: str