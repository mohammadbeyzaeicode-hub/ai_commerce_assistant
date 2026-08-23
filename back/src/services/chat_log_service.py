# core/chat/chat_log_service.py
# from core.chat.dto import ChatMessageDTO
# from repositories import (
#     ChatSessionRepository,
#     ChatMessageRepository,
# )

from datetime import datetime
from back.src.models.Enum.enum import ChatState, SenderType
from back.src.models.chat_session import ChatSession
from back.src.models.data_class.dataClass import IncomingMessage
from back.src.repositories.caht_message_repository import ChatMessageRepository
from back.src.repositories.chatSession_repository import ChatSessionRepository
from back.src.services.integrations.context import RequestContext


class ChatLogService:

    def __init__(
        self,
        session_repo: ChatSessionRepository,
        message_repo: ChatMessageRepository,
    ):
        self.session_repo = session_repo
        self.message_repo = message_repo

    async def append_message(
        self,
        session_key,
        role,
        sender_type=None,
        content=None,
        meta=None,
    ):
        session = await self.session_repo.get_or_create(
            tenant_id=session_key.tenant_id,
            external_user_id=session_key.user_id,
            channel=session_key.channel,
        ) 

        return await self.message_repo.add_message(
            session=session,
            role=role,
            sender_type=sender_type,
            content=content,
            meta=meta,
        )
   
    async def update_session(
        self,
        session_key:str,
        *,
        state: ChatState | None = None,
        assigned_agent_id: str | None = None,
        last_activity_at: datetime | None = None,
    ) -> ChatSession | None:
        session = await self.session_repo.get_by_session_key(
            tenant_id=session_key.tenant_id,
            external_user_id=session_key.user_id,
            channel=session_key.channel,
        )

        if not session:
            return None

        # ✅ اعمال Business Rules
        if state is not None:
            session.state = state

        if assigned_agent_id is not None:
            session.assigned_agent_id = assigned_agent_id

        if last_activity_at is not None:
            session.last_activity_at = last_activity_at

        # ✅ فقط persist
        return await self.session_repo.save(session)
        
    async def load_history(self, session_key, limit=None):
        session = await self.session_repo.get_by_session_key(
            tenant_id=session_key.tenant_id,
            external_user_id=session_key.user_id,
            channel=session_key.channel,
        )
        if not session:
            return []

        return await self.message_repo.get_history(session.id, limit)
    
    async def resolve_target_session(self,incoming_message:IncomingMessage,context:RequestContext) -> ChatSession | None:
     
     #buyer
        if not await self.is_user_seller(context):
            return await self.session_repo.get_or_create(context.tenant_id,incoming_message.external_user_id,incoming_message.channel)
    
     #seller
        # 2️⃣ Explicit binding (reply, /take, inline action)
        if incoming_message.metadata.get("session_id"):
            return await self.session_repo.get_by_id(incoming_message.metadata["session_id"])
        # # 3️⃣ Seller commands
        # if intent == SellerIntent.COMMAND:
        #     return None  # یا session خاص سیستم

        # # 4️⃣ Seller acting as support (explicit!)
        # if intent == SellerIntent.SUPPORT:
        #     active = self.session_repo.find_human_active_session(
        #         seller_id=incoming_message.sender_id
        #     )
        #     if not active:
        #         raise NoActiveSupportSession()
        #     return active

        if incoming_message.sender_type == SenderType.HUMAN:
            active =await self.session_repo.find_human_active_session(incoming_message.external_chat_id)
            if active:
                return active
        
        return await self.session_repo.get_or_create(context.tenant_id,incoming_message.external_user_id,context.channel)
    
    async def get_seller_and_user_id(self,incoming_message:IncomingMessage,context:RequestContext) -> ChatSession | None:
        session =await self.resolve_target_session(incoming_message,context)
        seller=session.assigned_human_id
        user=session.external_user_id
        return user,seller
    
    async def is_user_seller(self,context:RequestContext):
        return context.seller_id==context.user_id