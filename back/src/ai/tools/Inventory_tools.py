from typing import Dict
from .base import BaseTool
from back.src.models.product.aplication.services.product_service import ProductService


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

    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    async def __call__(self, product_id: int) -> Dict:
        product = await self.product_service.get_product(product_id)
        if not product:
            return {"error": "Product not found"}

        return {
            "product_id": product["id"],
            "name": product["name"],
            "inventory": product.get("inventory", 0)
        }
