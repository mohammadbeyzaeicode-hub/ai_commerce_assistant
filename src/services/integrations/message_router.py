from dataclasses import dataclass, field
from enum import Enum
from functools import partial
from typing import Tuple


from ai.orchestrator_new import LLMOrchestrator
from models.Enum.enum import ChatState, SenderType
from models.chat_session import ChatSession
from models.clasess.CommandResult import Audience, CommandResult, MessageIntent, MessageResponse , SendAndBindMessage, UIMode ,UIAction
from models.data_class.dataClass import IncomingMessage
from services.chat_log_service import ChatLogService
from services.integrations.context import RequestContext

from repositories.caht_message_repository import ChatMessageRepository
from repositories.chatSession_repository import ChatSessionRepository
from repositories.storeChannel_repository import StoreChannel_repository
from repositories.store_repository import StoreRepository
from services.integrations.context import RequestContext


from services.store_service import TenantResolver
from sessions.dbSessionBackend import DbSessionBackend
from sessions.json_backend import JsonSessionBackend
from core.key import SessionKey
from sessions.memory import InMemorySession
from ai.tools.order_tools import CreateOrderTool
from ai.tools.product_tools import CreateProductTool , CheckInventoryTool, SearchInventoryTool, UpdateProductTool
from ai.tools.seller.seller_tools import SellerTools
from core.settings import settings
from repositories import product_repository
from repositories.order_repository import SqlAlchemyOrderRepository
from repositories.product_repository import ProductRepository
from services import chat_log_service, order_service, product_service
from core.db import SessionLocal
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent 

class MessageRouter:
    def __init__(self,
                 chat_log_service:ChatLogService,
                 
                 send_to_user=None,
                 ):
        self.send_to_user=send_to_user       
        self.chat_log_service = chat_log_service
        self._handle_human_command = None
        self.dbsession = SessionLocal()
        self.seller_id=None
        self.user_id=None
        self.tools = {
    "check_inventory": CheckInventoryTool(),
    "create_product": CreateProductTool(),
    "update_product": UpdateProductTool(),    
    "create_order": CreateOrderTool(),
    "search_inventory": SearchInventoryTool(),
    "message_seller"  :SellerTools(send_to_user=send_to_user)
        }
        
        # تزریق Session Backend و Orchestrator
        # self.session_backend = InMemorySession
        self.session_backend_cls = partial(JsonSessionBackend, f"{BASE}/DB/sessions.json")
        # self.session_backend_cls = DbSessionBackend()
        

    @staticmethod
    def is_request_human(text: str) -> bool:
        text = text.lower().strip()
        return text in {
            "/support",
            "پشتیبانی",
            "صحبت با انسان",
            "فروشنده",
            "human",
            "support",
        }
    async def _load_session(self, message: IncomingMessage) -> ChatSession:
        # with self.dbsession as db_session:
        #     session_repo = ChatSessionRepository(db_session)
        #     session = await session_repo.get_or_create(
        #         tenant_id=message.tenant_id,
        #         external_user_id=message.external_chat_id,
        #         channel=message.channel,
        #     )
        #     return session
        pass
    
    
    async def handle(self,incoming_message:IncomingMessage,channel_ref)-> Tuple[CommandResult,ChatSession]:
        chat_id=incoming_message.external_chat_id
        text=incoming_message.text
        with self.dbsession as db_session:

# Repoها
            order_repo = SqlAlchemyOrderRepository(db_session)
            product_repo = ProductRepository(db_session)
            st_channel_repo = StoreChannel_repository(db_session)
            store_repo = StoreRepository(db_session)

            # Services
            order_serv = order_service.OrderService(order_repo)
            product_serv = product_service.ProductService(product_repo)

            # ChatLog
            # session_repo = ChatSessionRepository(db_session)
            # message_repo = ChatMessageRepository(db_session)
            # chat_log_serv = chat_log_service.ChatLogService(session_repo, message_repo)
            # self.chat_log_service = chat_log_serv
            # Tenant
            tenant_id = await TenantResolver(st_channel_repo).resolve(
                channel=incoming_message.channel,
                channel_ref=channel_ref
            )

            session_key = SessionKey(
                tenant_id=tenant_id,
                user_id=str(chat_id),
                channel=incoming_message.channel,
            )
            
            # selerId=  store_repo.get_seler_id(tenant_id)
            
            context = RequestContext(
                tenant_id=tenant_id,
                user_id=chat_id,
                seller_id=store_repo.get_seler_id(tenant_id),
                channel=incoming_message.channel
            )
            self.seller_id=context.seller_id
            self.user_id=context.user_id
            #bind service tools to use services
            self.tools["check_inventory"].set_service_provider(
                lambda: product_serv
            )
            self.tools["search_inventory"].set_service_provider(
                lambda: product_serv
            )
            self.tools["create_product"].set_service_provider(
                lambda: product_serv
            )
            self.tools["update_product"].set_service_provider(
                lambda: product_serv
            )
            self.tools["create_order"].set_service_provider(
                lambda: order_serv
            )
           
            # chat_session=await chat_log_serv.session_repo.get_or_create(
            #     context.tenant_id,
            #     context.user_id,
            #     context.channel
            # )
            chat_Session=await self.chat_log_service.resolve_target_session(incoming_message,context)
            
            # sender_type=SenderType.HUMAN  if context.user_id==context.seller_id else SenderType.USER 
                
            # ✅ Orchestrator اینجاست
            orchestrator = LLMOrchestrator(
                api_key=settings.GAPGPT_API_KEY,
                session_backend=self.session_backend_cls,
                tools=self.tools,
                chat_log_service=self.chat_log_service,
                context=context,
                sender_type=incoming_message.sender_type,
            )

            print("User ID:", chat_id)
        # chat_Session=await chat_log_serv.session_repo.get_or_create(
        #     context.tenant_id,
        #     context.user_id,
        #     context.channel
        # )  
            result = await self.route(
                                    text=text,
                                    session_key=session_key,
                                    context=context,
                                    sender_type=incoming_message.sender_type,
                                    orchestrator=orchestrator,
                                    chat=chat_Session,
                                    incoming=incoming_message,
                                    # send_to_user=self.send_to_user,
                                    # send_to_human=self.send_to_human,
                                    # send_notif_user=self.send_notif_user,
                                    # send_notif_seller=self.send_notif_seller,
                            
                                )
            return result,chat_Session
            
    async def _route_by_sender(
    self,
    message: IncomingMessage,
    session: ChatSession
) -> None:
        pass
    
    # dispatch to orchestrator
    async def _dispatch(
    self,
    message: IncomingMessage,
    session: ChatSession
) -> None:  
        pass
    
    
        






    async def _handle_user_human_request(
        self,
        chat:ChatSession,
        incoming:IncomingMessage
        
    ) -> CommandResult:
        if chat.state in (
            # ChatState.WAITING_FOR_HUMAN,
            ChatState.HUMAN_ACTIVE,
        ):
            return CommandResult(
                handled=True,
                messages=[MessageResponse(
                    target=Audience.USER,
                    text="✅ شما در حال حاضر به فروشنده متصل هستید."
                )]
            )
        if chat.state==ChatState.WAITING_FOR_HUMAN:
            return CommandResult(
                handled=True,
                messages=[MessageResponse(
                    target=Audience.USER,
                    text="✅درخواست شما قبلا ثبت شد، به‌زودی فروشنده پاسخ می‌دهد."
                )]
            )
        chat.state = ChatState.WAITING_FOR_HUMAN
        await self.chat_log_service.session_repo.save(chat)
        
        return CommandResult(
            handled=True,

            # 1️⃣ پیام به کاربر
            messages=[
                MessageResponse(
                    target=Audience.USER,
                    text="⏳ درخواست شما ثبت شد، به‌زودی فروشنده پاسخ می‌دهد."
                ),
                # 2️⃣ پیام به فروشنده (قابل bind)
                MessageResponse(
                    target=Audience.SELLER,
                    text=f"📥 درخواست جدید گفتگو\nSession: {chat.id}",
                    intent=MessageIntent(
                        kind="bindable",
                        purpose="seller_notification_for_chat"
                    )
                ),
            ],

            # 3️⃣ UI
            ui_actions=[
                UIAction(
                    target=Audience.USER,
                    mode=UIMode.NORMAL
                ),
                UIAction(
                    target=Audience.SELLER,
                    mode=UIMode.SELLER_PENDING
                )
            ],

            # 4️⃣ effects فقط دامنه‌ای
            effects=[]
        )

    async def route(
        self,
        *,
        text: str,
        session_key,
        context: RequestContext,
        sender_type: SenderType,
        chat:ChatSession,
        orchestrator: LLMOrchestrator | None = None,
        incoming:IncomingMessage,
        # send_to_user=None,
        # send_to_human=None,
    ) -> CommandResult:
        """
        send_to_user(text: str)
        send_to_human(text: str)
        """
        # 0️⃣ Start → درخواست انسان
        if  text.startswith("/start"):
            result = CommandResult(
                handled=True,
                messages=[MessageResponse(
                    target=Audience.USER,
                    text="به فروشگاه ما خوش امدید"
                )],
                ui_actions=[UIAction(
                    target=Audience.USER,
                    mode=UIMode.NORMAL
                )]
            )
            return result

        # 0️⃣ USER → درخواست انسان
        if sender_type == SenderType.USER and self.is_request_human(text):
            result = await self._handle_user_human_request(
                chat,
                incoming=incoming
            )
            return result

        # 0️⃣ COMMAND (فقط Human)
        if sender_type == SenderType.HUMAN and text.startswith("/"):
            
            self._handle_human_command = HumanCommandHandler(
            chat_log_service=self.chat_log_service
            )
            result = await self._handle_human_command.handle(
                command=text,
                chat=chat,
                context=context,
            )

            return result

        
        
        # 1️⃣ BOT_ACTIVE
        if chat.state == ChatState.BOT_ACTIVE:
            if not orchestrator:
                return CommandResult(handled=False)

            reply = await orchestrator.run(
                text,
                session_key,
                sender_type=sender_type,
            )

            return CommandResult(
                handled=True,
                messages=[
                    MessageResponse(
                        target=Audience.USER,
                        text=reply
                    )
                ]
            )

        # 2️⃣ WAITING_FOR_HUMAN
        if chat.state == ChatState.WAITING_FOR_HUMAN:
            self.chat_log_service.append_message(
                session_key=session_key,
                role="user",
                sender_type=sender_type,
                content=text,
            )

            return CommandResult(
                handled=True,
                messages=[
                    MessageResponse(
                        target=Audience.USER,
                        text=f"⏳ درخواست شما برای فروشنده ارسال شد، لطفاً منتظر بمانید."
                    )
                ]
            )

        # 3️⃣ HUMAN_ACTIVE
        if chat.state == ChatState.HUMAN_ACTIVE:

            # User → Human
            if sender_type == SenderType.USER:
                return CommandResult(
                    handled=True,
                    messages=[MessageResponse(
                        target=Audience.SELLER,
                        text=f"👤 مشتری:\n{text}"
                    )],
                )

            # Human → User
            if sender_type == SenderType.HUMAN:
                return CommandResult(
                    handled=True,
                    messages=[MessageResponse(
                        target=Audience.USER,
                        text=f"🧑‍💼 فروشنده:\n{text}"
                    )],
                )
#------------------------------------------------------

# --------------------------------------------------



class HumanCommandHandler:
    def __init__(self, chat_log_service: ChatLogService):
        self.chat_log_service = chat_log_service

    async def handle(self, command: str, chat, context:RequestContext) -> CommandResult:
        if not command.startswith("/"):
            return CommandResult(handled=False)

        if command == "/take":
            return await self.take(chat, context)

        if command == "/done":
            return await self.done(chat, context)

        if command == "/help":
            return self.help()

        return CommandResult(
            handled=True,
            messages=[]
            )

    async def take(self, chat:ChatSession, context:RequestContext) -> CommandResult:
        if chat.state == ChatState.HUMAN_ACTIVE:
            return CommandResult(
                handled=True,
                  messages=[
                MessageResponse(
                    target=Audience.SELLER,
                    text="✅ این چت قبلاً در اختیار فروشنده است."
                )
             ]
         )

        chat.state = ChatState.HUMAN_ACTIVE
        chat.assigned_human_id = context.seller_id
        await self.chat_log_service.session_repo.save(chat)

        return CommandResult(
            handled=True,
            messages=[
                MessageResponse(
                    target=Audience.SELLER,
                    text="✅ شما اکنون این چت را در اختیار دارید."
                ),
                MessageResponse(
                    target=Audience.USER,
                    text="✅ چت اکنون در اختیار فروشنده است."
                )
             ],
            ui_actions=[
            UIAction(
                target=Audience.SELLER,
                mode=UIMode.SELLER_ACTIVE   # ← این یعنی دکمه Done ظاهر شود
            )
        ]
         )

    async def done(self, chat:ChatSession, context:RequestContext) -> CommandResult:
        if chat.state != ChatState.HUMAN_ACTIVE:
            return CommandResult(
                handled=True,
                 messages=[
                    MessageResponse(
                        target=Audience.SELLER,
                        text="⚠️ این چت در اختیار انسان نیست."
                    )
                ]
            )

        if chat.assigned_human_id != context.seller_id:
            return CommandResult(
                handled=True,
                messages=[
                    MessageResponse(
                        target=Audience.SELLER,
                        text="❌ این چت در اختیار شما نیست."
                    )
                ]
            )
            

        chat.state = ChatState.BOT_ACTIVE
        chat.assigned_human_id = None
        await self.chat_log_service.session_repo.save(chat)

        return CommandResult(
            handled=True,
            messages=[
                MessageResponse(
                    target=Audience.SELLER,
                    text="✅ چت به Bot بازگردانده شد."
                ),
                MessageResponse(
                    target=Audience.USER,
                    text="✅ چت به Bot بازگردانده شد."
                )
            ],
            ui_actions=[
                UIAction(target=Audience.SELLER, mode=UIMode.NORMAL),
                UIAction(target=Audience.USER, mode=UIMode.NORMAL),
            ]
        )

    def help(self) -> CommandResult:
        return CommandResult(
            handled=True,
            messages=[
                MessageResponse(
                    target=Audience.SELLER,
                    text=(
                        "دستورات موجود:\n"
                        "/take - گرفتن چت برای پاسخگویی\n"
                        "/done - پایان دادن به پاسخگویی و بازگرداندن به Bot\n"
                        "/help - نمایش این پیام کمک"
                    )
                )
            ]
        )
