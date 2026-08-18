from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from core.db import Base


class ReplyMessageBinding(Base):
    __tablename__ = "reply_message_bindings"

    id = Column(Integer, primary_key=True)

    platform = Column(String(32), nullable=False)          # telegram / instagram / web
    external_message_id = Column(String(128), nullable=False)
    session_id = Column(String(64), nullable=False)

    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index(
            "ix_reply_message_lookup",
            "platform",
            "external_message_id",
        ),
    )
