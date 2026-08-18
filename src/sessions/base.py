# from abc import ABC, abstractmethod


# class SessionBackend(ABC):
#     @abstractmethod
#     def get_history(self, chat_id: str):
#         pass

#     @abstractmethod
#     def append(self, chat_id: str, role: str, content: str=None, name: str = None):
#         pass

from typing import Protocol
from core.key import SessionKey


class SessionBackend(Protocol):
    def append(
        self,
        key: SessionKey,
        role: str,
        content: str | None = None,
        **extra
    ) -> None:
        ...

    def get_history(self, key: SessionKey) -> dict: ...
    def clear(self, key: SessionKey) -> None: ...
