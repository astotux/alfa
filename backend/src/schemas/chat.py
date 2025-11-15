from pydantic import BaseModel

class CreateChat(BaseModel):
    question: str
    id: str
    
class CreateMessage(BaseModel):
    chatId: str
    content: str