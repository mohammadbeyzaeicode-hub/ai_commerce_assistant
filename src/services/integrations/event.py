from dataclasses import dataclass
from typing import Literal, Optional


@dataclass(frozen=True)
class Event:
    type: Literal["message", "callback"]
    chat_id: int
    user_id: int


@dataclass(frozen=True)
class MessageEvent(Event):
    text: str
    reply_to_message_id: Optional[int] = None
    replied_text: Optional[str] = None


@dataclass(frozen=True)
class CallbackEvent(Event):
    data: str
    message_id: int
