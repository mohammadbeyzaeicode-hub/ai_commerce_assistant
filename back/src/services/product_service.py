from itertools import product
from typing import Optional, List, Dict
from back.src.models.product import Product
from back.src.repositories.product_repository import ProductRepository
from back.src.repositories.sqlalchemy_base_repository import SqlAlchemyRepository


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def get_product(self, product_id: int, store_id: int) -> Optional[Product]:
        # return await self.product_repo.get_by_id(product_id, store_id)
        return await self.product_repo.get_by_id_unique_store(product_id, store_id)

    async def search_products_by_name(self, name: str) -> List[Product]:
        return await self.product_repo.search_products_by_name(name)

    async def list_products(self) -> List[Product]:
        return await self.product_repo.get_all()

    # async def create_product(self, data: Dict) -> Product:
        # محل عالی برای افزودن validation در آینده
        # return await self.product_repo.create(data)
    
    async def create_product(
        self,
        name: str,
        price: float,
        store_id: int,
        inventory: int = 0,
    ) -> Product:

        if price <= 0:
            raise ValueError("price must be positive")

        product = Product(
            name=name,
            price=price,
            inventory=inventory,
            store_id=store_id,            
        )
        return await self.product_repo.add(product)


    async def update_product(self, product_id: int,
        name: Optional[str] = None,
        price: Optional[float] = None,
        store_id: Optional[int] = None,
        inventory: Optional[int] = None,
        ) -> Optional[Product]:
        
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            return None
        # 2️⃣ فقط فیلدهایی که مقدار دارند را آپدیت کن
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if store_id is not None:
            product.store_id = store_id
        if inventory is not None:
            product.inventory = inventory
        
        return await self.product_repo.save(product)  
    
    async def delete_product(self, product_id: int) -> bool:
        return await self.product_repo.delete(product_id)
