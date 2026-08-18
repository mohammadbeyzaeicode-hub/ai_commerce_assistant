from ast import Dict
import asyncio
from dataclasses import dataclass
from functools import partial
# from multiprocessing import context
from telegram.ext import ContextTypes, CommandHandler
from pathlib import Path
from typing import Optional
import aiohttp
from attrs import field
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update

from core.db import SessionLocal
from models.Enum.enum import SenderType
from models.data_class.dataClass import IncomingMessage
from repositories.caht_message_repository import ChatMessageRepository
from repositories.chatSession_repository import ChatSessionRepository
from repositories.storeChannel_repository import StoreChannel_repository
from repositories.store_repository import StoreRepository
from repositories.telegram_binding_repository import TelegramBindingRepository
from services import chat_log_service
from services.integrations.context import RequestContext
from services.integrations.event import CallbackEvent, Event, MessageEvent
from services.integrations.message_router import MessageRouter
from services.store_service import TenantResolver
from services.telegram_binding_service import ReplyMessageBindingServiceImpl
from services.adapter.telegramAdapter import TelegramAdapter,TelegramEffectExecutor,CommandResultExecutor


BASE = Path(__file__).resolve().parent.parent.parent 

 
from telegram.request import HTTPXRequest

# proxy_url="http://127.0.0.1:4108"
class TelegramPoller:
    def __init__(self, bot_token: str):
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.offset = 0
        self.bot_token=bot_token
        # request = HTTPXRequest(
        #     proxy="http://127.0.0.1:5923",
        #     # proxy="SOCKS://127.0.0.1:5922",
        #     connect_timeout=10,
        #     read_timeout=20,     # کوتاه‌تر بهتر
        #     write_timeout=20,
        #     pool_timeout=20,
        #     http_version="1.1",
        # )
        self.bot= Bot(token=bot_token
                    #   ,request=request
                      )
     
        # try:
        #     bot = db.query(Bot).filter(Bot.id == bot_id).one()
        # finally:
        #     db.close()
        self.seller_id=None
        self.user_id=None
        self.tel_repo= TelegramBindingRepository
        self.reply_binding_service= ReplyMessageBindingServiceImpl(tel_repo=self.tel_repo)

    # async def get_updates(self, session): 
    #     url = f"{self.base_url}/getUpdates?timeout=10&offset={self.offset}"
    #     async with session.get(url,timeout=aiohttp.ClientTimeout(total=30)) as resp:
    #         return await resp.json() 
    async def get_updates(self):
        updates = await self.bot.get_updates(offset=self.offset, timeout=30)
        if updates:
            self.offset = updates[-1].update_id + 1
        return updates
    # async def send_message(self, session, chat_id: int, text: str):
    #     url = f"{self.base_url}/sendMessage"
    #     payload = {"chat_id": chat_id, "text": text}

    #     async with session.post(url, json=payload) as resp:
    #         data = await resp.json()
    #         return data
        
    async def start(self):
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
            sock_read=20
)
        print("Telegram Poller started...")
        # async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
                try:
                    # updates = await self.get_updates(session)
                    updates = await self.get_updates()
                    
                    
                    # if "result" in updates:
                    for update in updates:
                            
                            self.offset = update.update_id + 1
                            event = await self.build_event(update)
                            if not event:
                                continue
                            with SessionLocal() as db_session:   
                                sender_type=SenderType.HUMAN if self.seller_id==str(event.user_id) else SenderType.USER
                                
                                #store_repo
                                st_channel_repo = StoreChannel_repository(db_session)
                                store_repo = StoreRepository(db_session)
                                
                                
                                # Tenant
                                tenant_id = await TenantResolver(st_channel_repo).resolve(
                                    channel="telegram",
                                    channel_ref=self.bot_token
                                )
                                #context
                                context = RequestContext(
                                    tenant_id=tenant_id,
                                    user_id=event.user_id,
                                    seller_id=store_repo.get_seler_id(tenant_id),
                                    channel="telegram"
                                )
                                
                                is_seller= context.seller_id == event.user_id
                                sender_type = SenderType.USER if not is_seller else SenderType.HUMAN
                                # r=await self.handle_event(event,sender_type)
                                # if r=="back":
                                #     continue
                                
                                if not update.message and not update.callback_query:
                                    continue

                                if update.callback_query:
                                    text = event.data
                                    chat_id = event.chat_id
                                    user_id = event.user_id

                                    reply_to_message_id = event.message_id
                                    replyed_text = None

                                elif update.message:
                                    chat_id = event.chat_id
                                    user_id = event.user_id
                                    text = event.text

                                    reply_to_message_id = event.reply_to_message_id
                                    replyed_text = event.replied_text
                                
                                if reply_to_message_id is not None: 
                                    binded_session_id = await self.reply_binding_service.resolve(
                                        session=db_session,
                                        platform="telegram",
                                        reply_to_message_id=str(reply_to_message_id),
                                    )
                                else:
                                    binded_session_id = None    
                                 # ChatLog
                                session_repo = ChatSessionRepository(db_session)
                                message_repo = ChatMessageRepository(db_session)
                                chat_log_serv = chat_log_service.ChatLogService(session_repo, message_repo)
                                self.chat_log_service = chat_log_serv
                                
                                incoming = IncomingMessage(
                                    channel="telegram",
                                    sender_type=sender_type,
                                    text=text,
                                    external_chat_id=chat_id,
                                    external_user_id=str(chat_id),
                                    metadata={
                                        "reply_to_message_id": reply_to_message_id,
                                        "replyed_text": replyed_text,
                                        "session_id": binded_session_id,
                                    }
                                )
                                user_id,assined_id=await self.chat_log_service.get_seller_and_user_id(incoming,context)
                                self.seller_id=assined_id
                                if self.seller_id is None :
                                    self.seller_id=context.seller_id
                                    
                                self.user_id=user_id
                                
                                #router
                                router = MessageRouter(
                                    chat_log_service=self.chat_log_service,
                                    send_to_user = partial(self.send_message_, chat_id=self.user_id),
                                      # send_and_bind_message = lambda msg: self.send_and_bind_message(
                                    #     msg,
                                    #     session_id=session_id,
                                    #     chat_id=chat_id
                                    # )
                                )
                                router_result,chat_session=await router.handle(incoming_message=incoming,channel_ref=self.bot_token)
                                tel_adapter=TelegramAdapter(bot=self.bot )
                                effect_executor=TelegramEffectExecutor(adapter=tel_adapter, binding_service=self.reply_binding_service)
                                command_executer=CommandResultExecutor(tel_adapter,effect_executor)
                                await command_executer.run(db_session,router_result,chat_session,context)
                            # await router.route(
                            #     text=text,
                            #     session_key=session_key,
                            #     context=context,
                            #     sender_type=sender_type,
                            #     orchestrator=orchestrator,
                            #     chat=chat_Session,
                            #     send_to_user=lambda msg: self.send_message(session, chat_id, msg),
                            #     send_to_human=self.send_to_human,  # بعداً وصل می‌کنی
                          
                            # )

                            

                            # LLM Orchestrator
                            # reply =await orchestrator.run(text, session_key)

                            # Send reply
                            # await self.send_message(session, chat_id, reply)

                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print("Polling error:", e)

                await asyncio.sleep(2)
    async def send_notif_user(self, text: str, chat_id: str,reply_markup=None):        
        msg=await self.bot.send_message(chat_id=chat_id, text=text,reply_markup=reply_markup,disable_notification=True)
        return msg.message_id 
    async def send_notif_seller(self, text: str, chat_id: str,reply_markup=None):    
        text = text   
        msg=await self.bot.send_message(chat_id=chat_id, text=text,reply_markup=reply_markup,parse_mode="HTML",disable_notification=False)
        return msg.message_id             
   
    async def send_message_(self, text: str, chat_id: str,reply_markup=None):        
        msg=await self.bot.send_message(chat_id=chat_id, text=text,reply_markup=reply_markup)
        return msg.message_id
    
    async def send_to_human(self, text: str,human_id:str="0",reply_markup=None):        
        await self.bot.send_message(chat_id=human_id, text=text,reply_markup=reply_markup)  
         
    async def send_and_bind_message(self, text:str, session_id:str, chat_id:int="0"):
        reply_markup = await self.Take_keyboard()
        telegram_message_id = await self.send_message_(chat_id=chat_id, text=text,reply_markup=reply_markup)
        with SessionLocal() as session:
            await self.reply_binding_service.bind(
                session=session,
                platform="telegram",
                external_message_id=str(telegram_message_id),
                session_id=session_id,
            ttl_seconds=3600,
        )
    async def edit_message_reply_markup(
        self,
        chat_id: int,
        message_id: int,
        reply_markup: dict | None = None
    ):
        url = f"https://api.telegram.org/bot{self.bot_token}/editMessageReplyMarkup"

        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": reply_markup
        }

        async with self.http_session.post(url, json=payload) as resp:
            data = await resp.json()

            if not data.get("ok"):
                raise RuntimeError(
                    f"editMessageReplyMarkup failed: {data}"
                )

            return data["result"]

    # async def send_and_bind_message(
    #     self,
    #     text: str,
    #     session_id: str,
    #     chat_id: int,
    # ):
    #     payload = {
    #         "chat_id": chat_id,
    #         "text": text,
    #         "reply_markup": {
    #             "inline_keyboard": [[
    #                 {
    #                     "text": "✅ Take",
    #                     "callback_data": f"take:{session_id}"
    #                 }
    #             ]]
    #         }
    #     }

    #     await self.http_session.post(
    #         f"{self.base_url}/sendMessage",
    #         json=payload,
    #     )

    
        
    async def _handle_callback(self, callback: dict):
        data = callback.get("data")  # "take:session123"
        if not data:
            return

        command, *args = data.split(":")

        if command == "take":
            session_id = args[0]

            await self.human_command_handler.take(
                session_id=session_id,
                telegram_user_id=callback["from"]["id"],
            )

            # جواب به تلگرام (loading رو می‌بنده)
            await self.answer_callback(callback["id"])
    async def answer_callback(self, callback_id: str):
        await self.http_session.post(
            f"{self.base_url}/answerCallbackQuery",
            json={
                "callback_query_id": callback_id
            }
        )
    async def create_user_menu(self):
        reply_keyboard = [
            # ['🏠 منوی اصلی', '📞 پشتیبانی'],
            # ['❌ بستن منو'],
            ['📞 پشتیبانی'],
            # ['🏠 منوی اصلی', '📞 پشتیبانی'],
            # ['🏠 منوی اصلی', '📞 پشتیبانی'],
            
         
            
        ]

        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,            
            # is_persistent=True,
            one_time_keyboard=True
            
        )
        return reply_markup
    async def create_seller_menu(self):
        reply_keyboard = [
            # ['🏠 منوی اصلی', '📞 پشتیبانی'],
            # ['❌ بستن منو'],
            # ['📞 پشتیبانی'],
            # ['🏠 منوی اصلی', '📞 پشتیبانی'],
            # ['🏠 منوی اصلی', '📞 پشتیبانی'],
         
            
        ]

        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,            
            # is_persistent=True,
            one_time_keyboard=True
            
        )
        return reply_markup
 
   
    async def confirm_keyboard():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تایید", callback_data="/take")]
            # ,[InlineKeyboardButton("❌ لغو", callback_data="cancel")]
        ])
    async def Take_keyboard(selfs):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تایید", callback_data="/take")]
            # ,[InlineKeyboardButton("❌ لغو", callback_data="cancel")]
        ])
    def closed_menu(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("☰ منو", callback_data="menu:open")]
        ])

    def open_menu(self):
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📞 پشتیبانی", callback_data="menu:support"),
                    InlineKeyboardButton("🛒 خرید", callback_data="menu:buy"),
                ],
                [
                    InlineKeyboardButton("📝 ثبت نام", callback_data="menu:register"),
                    InlineKeyboardButton("ℹ️ راهنما", callback_data="menu:help"),
                ],
                [InlineKeyboardButton("☰ بستن منو", callback_data="menu:close")]
            ])
        
    # async def show_welcome_menu(self,update, context: ContextTypes.DEFAULT_TYPE):   
    #     keyboard = [
    #         [InlineKeyboardButton("☰ منو", callback_data="show_menu")]
    #     ]
    #     reply_markup = InlineKeyboardMarkup(keyboard)
    #     context.user_data['menu_open'] = False  # حالت منو بسته
    #     await update.message.reply_text("به بات خوش آمدید! :", reply_markup=reply_markup)
   
    # # --- 2. هندل کلیک روی دکمه‌ها ---
    # async def button_handler(update: Update , context: ContextTypes.DEFAULT_TYPE):
    #     query = update.callback_query
    #     await query.answer()

    #     # دکمه اصلی منو
    #     if query.data == "toggle_menu":
    #     # بررسی وضعیت منو
    #         menu_open = context.user_data.get('menu_open', False)

    #         if not menu_open:
    #             # باز کردن منو
    #             submenu_buttons = [
    #                 [InlineKeyboardButton("📞 پشتیبانی", callback_data="support"),
    #                 InlineKeyboardButton("🛒 خرید", callback_data="buy")],
    #                 [InlineKeyboardButton("📝 ثبت نام", callback_data="register"),
    #                 InlineKeyboardButton("ℹ️ راهنما", callback_data="help")],
    #                 [InlineKeyboardButton("☰ منو", callback_data="toggle_menu")]  # دکمه اصلی دوباره
    #             ]
    #             markup = InlineKeyboardMarkup(submenu_buttons)
    #             context.user_data['menu_open'] = True
    #             await query.edit_message_reply_markup(reply_markup=markup)
    #         else:
    #             # بستن منو (فقط دکمه اصلی)
    #             keyboard = [[InlineKeyboardButton("☰ منو", callback_data="toggle_menu")]]
    #             markup = InlineKeyboardMarkup(keyboard)
    #             context.user_data['menu_open'] = False
    #             await query.edit_message_reply_markup(reply_markup=markup)

    #     # دکمه‌های زیرمنو
    #     elif query.data == "support":
    #         await query.answer("پیام به بات ارسال شد: پشتیبانی")
    #     elif query.data == "buy":
    #         await query.answer("پیام به بات ارسال شد: خرید")
    #     elif query.data == "register":
    #         await query.answer("پیام به بات ارسال شد: ثبت نام")
    #     elif query.data == "help":
    #         await query.answer("پیام به بات ارسال شد: راهنما")
    async def handle_event(self, event:Event, sender_type:SenderType  ):
        sender_type = sender_type
        if isinstance(event, MessageEvent):
            
            if event.text == "/start":
                reply_markup=await self.create_seller_menu() if sender_type==SenderType.HUMAN else await self.create_user_menu()
                await self.send_message_(
                    chat_id=event.chat_id,
                    text="به ربات خوش آمدید!",
                    reply_markup=reply_markup
                )
                return "back"

            # if event.text == "/support":
            #     await self.send_message_(
            #         chat_id=event.chat_id,
            #         text="ارتباط با پشتیبانی 👇"
            #     )
            #     return "back"

        elif isinstance(event, CallbackEvent):

            if event.data == "menu:open":
                await self.edit_message_reply_markup(
                    chat_id=event.chat_id,
                    message_id=event.message_id,
                    reply_markup=self.open_menu()
                ) 
                return "back"

            if event.data == "menu:close":
                await self.edit_message_reply_markup(
                    chat_id=event.chat_id,
                    message_id=event.message_id,
                    reply_markup=self.closed_menu()
                )
                return "back"   
         
            
    async def build_event(self, update: Update)->Event:
        # ──────────────────
    # CALLBACK QUERY
    # ──────────────────
        if update.callback_query:
            cb = update.callback_query
            msg = cb.message

            return CallbackEvent(
                type="callback",
                chat_id=msg.chat.id,
                user_id=cb.from_user.id,
                message_id=msg.message_id,
                data=cb.data or ""
            )
        
    # ──────────────────
    # MESSAGE
    # ──────────────────
        if update.message:
            msg = update.message
            text = msg.text or ""

            match text:
                case "📞صحبت با فروشنده":
                    text = "/support"
                case "پایان صحبت":
                    text = "/done"

            reply = msg.reply_to_message

            return MessageEvent(
                type="message",
                chat_id=msg.chat.id,
                user_id=msg.from_user.id,
                text=text,
                reply_to_message_id=reply.message_id if reply else None,
                replied_text=reply.text if reply else None
            )

        return None
