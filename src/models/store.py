from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from core.db import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # اگر بعداً seller/users داشتی
    owner_id = Column(Integer, nullable=True)

    is_active = Column(Boolean, nullable=False, server_default="1")
    created_at = Column(DateTime, server_default=func.now())

    channels = relationship(
        "StoreChannel",
        back_populates="store",
        cascade="all, delete-orphan",
    )
    products = relationship("Product", back_populates="store")

