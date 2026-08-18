from datetime import datetime, timezone, timedelta

from typing import Optional, List, Dict

from models.telegram_reply import ReplyMessageBinding
from models.user import User
from repositories.sqlalchemy_base_repository import SqlAlchemyRepository
from repositories.telegram_binding_repository import TelegramBindingRepository
from services.Interfaces.telegramBinding import ReplyMessageBindingService

class ReplyMessageBindingServiceImpl(ReplyMessageBindingService):

    def __init__(self, tel_repo: TelegramBindingRepository):
        self.tel_repo = tel_repo
  

    async def bind(
        self,
        *,
        session,
        platform: str,
        external_message_id: str,
        session_id: str,
        ttl_seconds: int = 3600,
    ) -> None:
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None)  + timedelta(seconds=ttl_seconds)
        repo=self.tel_repo(session)
        message=ReplyMessageBinding(
                    platform=platform,
                    external_message_id=external_message_id,
                    session_id=session_id,
                    expires_at=expires_at,
                )
        await repo.create_or_update(message= message )
         
        await repo.commit()
        await repo.refresh(message)

    async def resolve(
        self,
        *,
        session,
        platform: str,
        reply_to_message_id: str,
    ) -> str | None:
        repo=self.tel_repo(session)
        binding = await repo.get_by_external_message(
            platform=platform,
            external_message_id=reply_to_message_id,
        )

        if not binding:
            return None
        
        # تبدیل expires_at به aware (اگر naive است)
        if binding.expires_at.tzinfo is None:
            expires_at_aware = binding.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at_aware = binding.expires_at

        # if expires_at < datetime.utcnow():
        if  expires_at_aware < datetime.now(timezone.utc):
            await repo.delete_by_id(binding.id)
            return None

        return binding.session_id

    async def cleanup_expired(self,session) -> int:
        repo=self.tel_repo(session)
        return await repo.delete_expired(
            now=datetime.now(timezone.utc)
        )
    
    
    def get_last_message_id(
        self, *, platform: str, session_id: int, target: int
    ) -> int | None:
        ...    
