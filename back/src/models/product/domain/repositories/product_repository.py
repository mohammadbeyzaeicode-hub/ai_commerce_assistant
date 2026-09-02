from abc import ABC, abstractmethod
from typing import Optional
from ..entities.product import Product


class ProductRepository(ABC):

    @abstractmethod
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        pass

    @abstractmethod
    async def search_by_name(self, name: str) -> list[Product]:
        pass

    @abstractmethod
    async def get_by_id_unique_store(
        self,
        product_id: int,
        store_id: int
    ) -> Optional[Product]:
        pass

    @abstractmethod
    async def get_all_by_store(self, store_id: int) -> list[Product]:
        pass