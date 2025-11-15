from datetime import datetime

from sqlalchemy import (
    String, Text, DateTime, Enum, ForeignKey
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)
from .user import Base
import enum

class MessageRole(enum.Enum):
    user = "user"
    assistant = "assistant"


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[str] = mapped_column(
        String, primary_key=True
    )
    title: Mapped[str|None] = mapped_column(String, nullable=True)
    userId: Mapped[str] = mapped_column(String)

    createdAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String, primary_key=True
    )
    
    userId: Mapped[str] = mapped_column(String)
    
    chatId: Mapped[str] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE")
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole))
    content: Mapped[str] = mapped_column(Text)

    createdAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    chat: Mapped["Chat"] = relationship(
        back_populates="messages"
    )