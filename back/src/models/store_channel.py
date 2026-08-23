from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    JSON,
    func,
)
from sqlalchemy.orm import relationship
from back.src.core.db import Base


class StoreChannel(Base):
    __tablename__ = "store_channels"

    id = Column(Integer, primary_key=True)

    store_id = Column(
        Integer,
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
    )

    channel = Column(String(50), nullable=False)
    channel_ref = Column(String(255), nullable=False)

    settings = Column(JSON, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    store = relationship("Store", back_populates="channels")

    __table_args__ = (
        UniqueConstraint(
            "channel",
            "channel_ref",
            name="uq_store_channel_ref",
        ),
    )
