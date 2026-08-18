from abc import ABC, abstractmethod

class ReplyMessageBindingService(ABC):

    @abstractmethod
    async def bind(
        self,
        *,
        platform: str,
        external_message_id: str,
        session_id: str,
        ttl_seconds: int = 3600,
    ) -> None:
        ...

    @abstractmethod
    async def resolve(
        self,
        *,
        platform: str,
        reply_to_message_id: str,
    ) -> str | None:
        ...

    @abstractmethod
    async def cleanup_expired(self) -> int:
        ...
