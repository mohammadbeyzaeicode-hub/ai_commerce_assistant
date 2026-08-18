from models.order_item import OrderItem
from models.product import Product
from repositories.sqlalchemy_base_repository import SqlAlchemyRepository

class OrderItemRepository(SqlAlchemyRepository[OrderItem]):
    def __init__(self, session):
        super().__init__(session, OrderItem)
