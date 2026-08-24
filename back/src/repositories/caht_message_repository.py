from back.src.models.chat_message import ChatMessage
from back.src.infrastructure.database.repositories.sqlalchemy_base_repository import SqlAlchemyRepository


from typing import List
from sqlalchemy.orm import Session

from back.src.models import ChatMessage, ChatSession


class ChatMessageRepository(SqlAlchemyRepository[ChatMessage]):

    def __init__(self, session: Session):
        super().__init__(session, ChatMessage)

    async def add_message(
        self,
        session: ChatSession,
        role: str,
        sender_type: str,
        content: str | None,
        meta: dict | None = None,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session.id,
            role=role,
            sender_type=sender_type,
            content=content,
            meta=meta,
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    async def get_history(
        self,
        session_id: int,
        limit: int | None = None,
    ) -> List[ChatMessage]:
        q = (
            self.session.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )

        if limit:
            q = q.limit(limit)

        return q.all()
