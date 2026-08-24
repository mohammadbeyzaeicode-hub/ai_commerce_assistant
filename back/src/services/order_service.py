from typing import Optional, List, Dict
from back.src.models.order import Order
from back.src.infrastructure.database.repositories.sqlalchemy_base_repository import SqlAlchemyRepository



class OrderService:
    def __init__(self, order_repo: SqlAlchemyRepository[Order]):
        self.order_repo = order_repo

    async def get_order(self, order_id: int) -> Optional[Order]:
        return await self.order_repo.get_by_id(order_id)

    async def list_orders(self) -> List[Order]:
        return await self.order_repo.get_all()

    async def create_order(self, user_id: int, product_id: int, quantity: int) -> Order:
        # اینجا بعداً می‌تونیم:
        # - موجودی چک کنیم
        # - قیمت محاسبه کنیم
        # - وضعیت پرداخت اضافه کنیم
        order_data = {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
        }
        return await self.order_repo.create(order_data)

    async def update_order(self, order_id: int, data: Dict) -> Optional[Order]:
        return await self.order_repo.update(order_id, data)

    async def delete_order(self, order_id: int) -> bool:
        return await self.order_repo.delete(order_id)
