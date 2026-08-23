
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from back.src.core.db import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    # products = relationship("Product", back_populates="seller")     
    orders = relationship("Order", back_populates="user")
    # chat_sessions = relationship("ChatSession", back_populates="user")
