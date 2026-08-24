from back.src.models.order_item import OrderItem
from back.src.models.product.domain.entities.product import Product
from back.src.infrastructure.database.repositories.sqlalchemy_base_repository import SqlAlchemyRepository

class OrderItemRepository(SqlAlchemyRepository[OrderItem]):
    def __init__(self, session):
        super().__init__(session, OrderItem)
