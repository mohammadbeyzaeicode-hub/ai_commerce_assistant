from typing import Dict, Optional

from back.src.services import product_service
from .base import BaseTool
from back.src.services.product_service import ProductService


class CreateProductTool(BaseTool):
    name = "create_product"
    description = "Create a new product"
    arguments_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "price": {"type": "number"},
            "inventory": {"type": "integer"}
            
        },
        "required": ["name", "price"]
    }

    def __init__(self
                #  , product_service: ProductService
                 ):
        # self.product_service = product_service
        pass

    async def __call__(self, name: str, price: float,  inventory: int = 0) -> Dict:
        store_id = self.context.tenant_id
        product = await self.get_service().create_product(
            name=name,
            price=price,
            inventory=inventory,
            store_id=store_id
        )

        return {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "inventory": product.inventory,
            "store_id": product.store_id
        }

class UpdateProductTool(BaseTool):
    name = "update_product"
    description = "Update existing product"
    arguments_schema = {
        "type": "object",
        "properties": {
            "id":{"type": "integer"},
            "name": {"type": "string"},
            "price": {"type": "number"},
            "inventory": {"type": "integer"}
        },
        "required": ["id"]
    }

    def __init__(self
                #  , product_service: ProductService
                 ):
        # self.product_service = product_service
        pass

    async def __call__(self, id: int, name: Optional[str] = None, price: Optional[float] = None, inventory: Optional[int] = None) -> Dict:
        store_id = self.context.tenant_id

        product = await self.get_service().update_product(
            product_id=id,
            name=name,
            price=price,
            inventory=inventory,
            store_id=store_id
        )

        if not product:
            return {"error": "Product not found"}

        return {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "inventory": product.inventory,
            "store_id": product.store_id,
        }


class CheckInventoryTool(BaseTool):
    name = "check_inventory"
    description = "Check product inventory by product ID."
    arguments_schema = {
        "type": "object",
        "properties": {
            "product_id": {"type": "integer"}
        },
        "required": ["product_id"]
    }

    def __init__(self
                #  ,product_service: ProductService
                 ):
        # self.product_service = product_service
        pass

    async def __call__(self, product_id: int) -> Dict:
        store_id = self.context.tenant_id
        
        product = await self.get_service().get_product(product_id,store_id)
        if not product:
            return {"error": "Product not found"}

        return {
            "product_id": product.id,
            "name": product.name,
            "inventory": product.inventory,
            "price":product.price
        }

class SearchInventoryTool(BaseTool):
    name = "search_inventory"
    description = "Search product inventory by product name."
    arguments_schema = {
        "type": "object",
        "properties": {
            "product_name": {"type": "string"}
        },
        "required": ["product_name"]
    }

    def __init__(self
                #  , product_service: ProductService
                 ):
        # self.product_service = product_service
        pass

    async def __call__(self, product_name: str) -> Dict:
        products = await self.get_service().search_products_by_name(product_name)
        if not products:
            return {"error": "Product not found"}

        return [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "inventory": product.inventory,
                "store_id": product.store_id,
            }
            for product in products
        ]
