
from ast import Dict
from dataclasses import dataclass
from typing import Optional

from attrs import field

from back.src.models.Enum.enum import SenderType


@dataclass(frozen=True)
class IncomingMessage:
    channel: str                  # telegram / instagram / whatsapp / web
    external_chat_id: str          # conversation identifier in channel
    external_user_id: Optional[str]

    text: str
    sender_type: SenderType | None = None
    sender_id: Optional[str] = None

    metadata: Dict | None = field(default=dict)