from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from core.db import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)

    # Multi-tenant identity
    tenant_id = Column(String(100), nullable=False)
    external_user_id = Column(String(100), nullable=False)
    channel = Column(String(50), nullable=False)

    title = Column(String(200), nullable=True)

      
    # // for handle between bot and seller
    state = Column( String(30), nullable=False, default="BOT_ACTIVE", index=True, )     # BOT_ACTIVE, WAITING_FOR_HUMAN, HUMAN_ACTIVE, (اختیاری آینده) CLOSED
    assigned_human_id = Column( Integer,ForeignKey("users.id"), nullable=True, index=True, )
    last_activity_at = Column(DateTime, nullable=False, default=datetime.utcnow,index=True, )
    
    # //
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    __table_args__ = (
        Index(
            "ix_chat_session_tenant_extuser_channel",
            "tenant_id",
            "external_user_id",
            "channel",
            unique=True,
        ),
    )

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )
