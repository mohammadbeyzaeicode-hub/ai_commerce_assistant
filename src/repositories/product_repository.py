from models.product import Product
from repositories.sqlalchemy_base_repository import SqlAlchemyRepository


class ProductRepository(SqlAlchemyRepository[Product]):
    def __init__(self, session):
        super().__init__(session, Product)

    async def search_products_by_name(self, name: str):
        return (
            self.session.query(Product)
            .filter(Product.name.ilike(f"%{name}%"))
            .all()
        )
    async def get_by_id_unique_store(self, product_id: int, store_id: int):
        return (
            self.session.query(Product)
            .filter(Product.id == product_id, Product.store_id == store_id)
            .first()
        )    
