from .base import BaseTool
from back.src.services.order_service import OrderService

class CreateOrderTool(BaseTool):
    name = "create_order"
    description = "Create a new order ,"
    arguments_schema = {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer"},
            "user_name": {"type": "string"},
            "product_id": {"type": "integer"},
            "product_name": {"type": "string"},
            "inventory": {"type": "integer"},
        },
        "required": ["product_name", "inventory"]
    }

    def __init__(self
                #  , order_service: OrderService
                 ):
        # self.order_service = order_service
        pass

    async def __call__(self,  product_id: int, inventory: int,user_id: int=10):
        order = await self.get_service().create_order(user_id, product_id=product_id, inventory=inventory)
        if not order:
            return {"error": "Order creation failed"}

        return {
            "id": order.id,
            "user_id": order.user_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
        }
        # return await self.order_service.create_order(user_id, product_id, inventory)
