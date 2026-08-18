from asyncio import Protocol
from typing import Any

from models.clasess.CommandResult import UIMode


class TransportAdapter(Protocol):

    async def send_message(
        self,
        target_id: int,
        text: str,
        reply_markup: Any | None = None,
    ) -> Any: ...

    async def apply_ui(
        self,
        target_id: int,
        mode: UIMode,
    ) -> None: ...
    async def reset_ui(
        self,
        target_id: int,
    ) -> None: ...