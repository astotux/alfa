from datetime import datetime

from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import (
    Mapped, mapped_column
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    telegram_id = Column(Integer, nullable=True, unique=True, index=True)

    def __repr__(self):
        return f"<User {self.username}>"
