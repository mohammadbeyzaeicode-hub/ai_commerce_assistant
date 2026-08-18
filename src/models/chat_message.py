from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, String, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from core.db import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)

    session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role = Column(String(20), nullable=False, index=True) # for llm
    sender_type = Column(String(20), nullable=False, index=True) # ---->  user , bot , human , system

    content = Column(Text, nullable=True)

    meta = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    session = relationship(
        "ChatSession",
        back_populates="messages",
    )
