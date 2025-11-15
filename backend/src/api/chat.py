from datetime import datetime, timedelta
from uuid import uuid4

from another_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from auth.dependencies import get_current_user

from models.user import User
from database.database import get_db
from models.chat import Chat, Message, MessageRole
from schemas.chat import CreateChat, CreateMessage

router = APIRouter()


@router.post("/chat", status_code=status.HTTP_201_CREATED)
def create_chat(chat_data: CreateChat, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not chat_data.question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Введите текст сообщения"
        )
    
    chatExisted = db.query(Chat).filter(Chat.id == chat_data.id).first()
    if chatExisted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Чат с таким ID уже существует"
        )

    new_chat = Chat(
        id=chat_data.id,
        userId=user.id,
        title=chat_data.question,      
    )

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    user_msg = Message(
        id=str(uuid4()),
        chatId=new_chat.id,
        role=MessageRole.user,
        content=chat_data.question
    )

    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    return {
        "chatId": new_chat.id,
        "title": new_chat.title,
        "messages": [
            {
                "id": user_msg.id,
                "role": user_msg.role.value,
                "content": user_msg.content,
            },
        ]
    }

@router.get("/chats")
def get_user_chats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    chats = (
        db.query(Chat.id, Chat.title, Chat.createdAt, Chat.updatedAt)
        .filter(Chat.userId == user.id)
        .order_by(Chat.updatedAt.desc())
        .all()
    )

    return [
        {
            "id": c.id,
            "title": c.title,
            "createdAt": c.createdAt,
            "updatedAt": c.updatedAt,
        }
        for c in chats
    ]
    
@router.get("/chats/{chat_id}")
def get_current_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    chat = (
        db.query(Chat.id, Chat.title, Chat.createdAt, Chat.updatedAt)
        .filter(Chat.userId == user.id, Chat.id == chat_id)  # ✅ исправлено
        .order_by(Chat.updatedAt.desc())
        .first()
    )
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )

    return chat
    
@router.delete("/chat/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )

    if chat.userId != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому чату"
        )

    db.delete(chat)
    db.commit()

    return
  
@router.post("/messages", status_code=status.HTTP_201_CREATED)
def create_message(
    data: CreateMessage,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    chat = db.query(Chat).filter(Chat.id == data.chatId).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )

    if chat.userId != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому чату"
        )

    user_message = Message(
        id=str(uuid4()),
        chatId=chat.id,
        role=MessageRole.user,
        content=data.content
    )
    db.add(user_message)

    chat.updatedAt = datetime.utcnow()

    db.commit()
    db.refresh(user_message)

    # ai_answer = ask_ai(data.content)

    # ai_message = Message(
    #     id=str(uuid4()),
    #     chatId=chat.id,
    #     role=MessageRole.assistant,
    #     content=ai_answer
    # )
    # db.add(ai_message)
    # db.commit()
    # db.refresh(ai_message)

    return {
        "userMessage": {
            "id": user_message.id,
            "role": user_message.role.value,
            "content": user_message.content,
            "createdAt": user_message.createdAt
        },
    }