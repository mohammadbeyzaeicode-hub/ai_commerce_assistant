# core/chat/ports.py
from abc import ABC, abstractmethod
from back.src.core.key import SessionKey

class ChatSessionPort(ABC):

    @abstractmethod
    def get_history(self, session_key: SessionKey) -> dict:
        pass

    @abstractmethod
    def append(self, session_key: SessionKey, role: str, content: str | None, **kwargs):
        pass

    @abstractmethod
    def set(self, session_key: SessionKey, data: dict):
        pass
