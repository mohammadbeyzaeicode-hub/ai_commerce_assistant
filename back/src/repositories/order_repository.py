from sqlalchemy.orm import Session
from typing import Optional, List

from back.src.models.order import Order
from .base_repository import AbstractRepository


class SqlAlchemyOrderRepository(AbstractRepository):

    def __init__(self, session: Session):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[Order]:
        return self.session.get(Order, id)

    async def get_all(self) -> List[Order]:
        return self.session.query(Order).all()

    async def create(self, data: dict) -> Order:
        order = Order(**data)
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    async def update(self, id: int, data: dict) -> Optional[Order]:
        order = self.session.get(Order, id)
        if not order:
            return None

        for key, value in data.items():
            setattr(order, key, value)

        self.session.commit()
        return order

    async def delete(self, id: int) -> bool:
        order = self.session.get(Order, id)
        if not order:
            return False

        self.session.delete(order)
        self.session.commit()
        return True
