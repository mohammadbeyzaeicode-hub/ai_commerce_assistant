from back.src.models.Enum.enum import ChatState
from back.src.models.chat_session import ChatSession
from back.src.repositories.sqlalchemy_base_repository import SqlAlchemyRepository


from typing import Optional
from sqlalchemy.orm import Session

from back.src.models import ChatSession


class ChatSessionRepository(SqlAlchemyRepository[ChatSession]):

    def __init__(self, session: Session):
        super().__init__(session, ChatSession)

    async def get_by_session_key(
        self,
        tenant_id: str,
        external_user_id: str,
        channel: str,
    ) -> Optional[ChatSession]:
        return (
            self.session.query(ChatSession)
            .filter(
                ChatSession.tenant_id == tenant_id,
                ChatSession.external_user_id == external_user_id,
                ChatSession.channel == channel,
            )
            .first()
        )

    async def get_or_create(
        self,
        tenant_id: str,
        external_user_id: str,
        channel: str,
    ) -> ChatSession:
        session = await self.get_by_session_key(
            tenant_id, external_user_id, channel
        )
        if session:
            return session

        session = ChatSession(
            tenant_id=tenant_id,
            external_user_id=external_user_id,
            channel=channel,
        )
        self.session.add(session)
        self.session.commit()
        self.session.refresh(session)
        return session
    
    async def find_human_active_session(self,human_id: int) -> ChatSession | None:
        return (
            self.session.query(ChatSession)
            .filter(
                ChatSession.assigned_human_id == human_id,
                ChatSession.state == ChatState.HUMAN_ACTIVE,
            )
            .order_by(ChatSession.updated_at.desc())
            .first()
        )