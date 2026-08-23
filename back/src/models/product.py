# models/product_model.py
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from back.src.core.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    price = Column(Integer, nullable=False)  # تومان / ریال بعداً مشخص می‌شود
    is_active = Column(Boolean, default=True)

    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    inventory = Column(Integer, nullable=False, default=0)  # ✅ موجودی

    store = relationship("Store", back_populates="products")
