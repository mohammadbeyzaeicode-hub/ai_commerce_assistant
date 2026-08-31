from ...domain.entities.product import Product
from ...domain.repositories.product_repository import ProductRepository
from back.src.infrastructure.database.repositories.sqlalchemy_base_repository import (
    SqlAlchemyRepository
)


class SqlAlchemyProductRepository(
    SqlAlchemyRepository[Product],
    ProductRepository
):
    def __init__(self, session):
        super().__init__(session, Product)

    async def search_by_name(self, name: str):
        return (
            self.session.query(Product)
            .filter(Product.name.ilike(f"%{name}%"))
            .all()
        )

    async def get_by_id_unique_store(
        self,
        product_id: int,
        store_id: int
    ):
        return (
            self.session.query(Product)
            .filter(
                Product.id == product_id,
                Product.store_id == store_id
            )
            .first()
        )

    async def get_all_by_store(self, store_id: int):
        return (
            self.session.query(Product)
            .filter(Product.store_id == store_id)
            .all()
        )