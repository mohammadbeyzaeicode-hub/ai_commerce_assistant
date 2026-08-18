from typing import Protocol

class SellerMessenger(Protocol):
    async def send_message_(self, message: str): ...
