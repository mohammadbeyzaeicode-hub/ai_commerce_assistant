from typing import Dict

from back.src.ai.tools.interfaces import SellerMessenger
from back.src.services.integrations import telegram_poller

from ..base import BaseTool



class SellerTools(BaseTool):
    name = "message_seller"
    description = "Message the seller if needed or have problem and you must fill parameters."
    arguments_schema = {
        "type": "object",
        "properties": {
            "text": {"type": "string"}
        },
        "required": ["text"]
    }

    def __init__(self, send_to_user
                #  ,tel:SellerMessenger=None
                 ):
        super().__init__()
        self.send_message = send_to_user

    async def __call__(self, text) :
         await self.send_message(5142405088, text)

