from abc import ABC
from dataclasses import dataclass,field
from enum import Enum, auto
from typing import Literal



class UIMode(Enum):
    NORMAL = auto()
    SELLER_PENDING = auto()
    SELLER_ACTIVE = auto()
    

class Audience(Enum):
    USER = "user"
    SELLER = "seller"

@dataclass(frozen=True)
class UIAction:
    target: Audience
    mode: UIMode

@dataclass    
class MessageIntent:
    kind: Literal["bindable", "ask_reply", "info"]
    purpose: str | None = None

@dataclass
class MessageResponse:
    target: Audience  # 'seller' or 'user'
    text: str | None = None
    intent: MessageIntent | None = None
    


#-------------------------------------------------------------------
#Effect
class Effect(ABC):
    pass


@dataclass(frozen=True)
class SendMessage(Effect):
    audience: Audience
    text: str


@dataclass(frozen=True)
class SendAndBindMessage(Effect):
    audience: Audience
    text: str
    session_id: str


@dataclass(frozen=True)
class SaveState(Effect):
    key: str
    value: str


@dataclass(frozen=True)
class TriggerWebhook(Effect):
    url: str
    payload: dict
#-------------------------------------------------------------------


@dataclass
class CommandResult:
    handled: bool
    messages: list[MessageResponse] = field(default_factory=list)
    effects: list[Effect] = field(default_factory=list)
    ui_actions: list[UIAction] = field(default_factory=list)
    