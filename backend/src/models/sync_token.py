from datetime import datetime

from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .user import Base


class SyncToken(Base):
    __tablename__ = "sync_tokens"

    token: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    user_id: Mapped[str] = mapped_column("user_id", String, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime, default=datetime.now)

    def __repr__(self):
        return f"<SyncToken {self.token[:8]}...>"
