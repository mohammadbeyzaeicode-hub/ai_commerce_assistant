from aiohttp import ClientSession
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from back.src.models.chat_session import ChatSession
from back.src.models.clasess.CommandResult import Audience, CommandResult, Effect, SendAndBindMessage, UIAction, UIMode
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from sqlalchemy.orm import Session
from back.src.services import telegram_binding_service
from back.src.services.integrations.context import RequestContext


class TelegramAdapter:

    def __init__(self, bot:Bot):
        self.bot = bot
    async def send_message(
        self,
        target_id: int,
        text: str,
        ui_action:UIAction
    ):
        reply_markup=None
        if(ui_action):
            reply_markup=await self._build_keyboard(ui_action)
            
        return await self.bot.send_message(
            chat_id=target_id,
            text=text,
            reply_markup=reply_markup
        )
    async def _build_keyboard(self, action: UIAction):
        if action.target == Audience.USER:
            return await self._user_keyboard(action.mode)

        if action.target == Audience.SELLER:
            return await self._seller_keyboard(action.mode)    
    async def _seller_keyboard(self, mode: UIMode):
        match mode:
            case UIMode.NORMAL:
                # kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
                # kb.add(KeyboardButton("📞صحبت با فروشنده"))
                # return kb
                kb=ReplyKeyboardRemove()
                return kb

            case UIMode.SELLER_PENDING:
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ تایید", callback_data="/take")]
                    # ,[InlineKeyboardButton("❌ لغو", callback_data="cancel")]
                ])
                # kb.add(KeyboardButton("پذیرش درخواست"))
                return kb

            case UIMode.SELLER_ACTIVE:
                keyboard=[[KeyboardButton("پایان صحبت")]]
                kb = ReplyKeyboardMarkup(keyboard=keyboard,
                                         resize_keyboard=True,one_time_keyboard=True)
                return kb
    async def _user_keyboard(self, mode: UIMode):
        match mode:
            case UIMode.NORMAL:
                keyboard=[[KeyboardButton("📞صحبت با فروشنده")]]
                kb = ReplyKeyboardMarkup(keyboard=keyboard,
                                         resize_keyboard=True,one_time_keyboard=True)
                return kb

            case UIMode.SELLER_PENDING:
                # kb = ReplyKeyboardMarkup(resize_keyboard=True)
                # kb.add(KeyboardButton("/take"))
                return None

            case UIMode.SELLER_ACTIVE:
                # kb = ReplyKeyboardMarkup(resize_keyboard=True)
                # kb.add(KeyboardButton("/done"))
                # return kb
                return None
    
    async def apply_ui(self, target_id: int, message_id:int,action: UIAction):
        keyboard =await self._build_keyboard(action)
        LAST_BOUND_MESSAGE_ID=message_id
        await self.bot.edit_message_reply_markup(
            chat_id=target_id,
            message_id=LAST_BOUND_MESSAGE_ID,               # پیام خالی برای UI update
            reply_markup=keyboard
        )
   
class CommandResultExecutor:

    def __init__(
        self,
        adapter: TelegramAdapter,
        effect_executor: "TelegramEffectExecutor",
    ):
        self.adapter = adapter
        self.effect_executor = effect_executor
    async def run(
        self,
        db_session:Session,
        result: CommandResult,
        chat: ChatSession,
        context: RequestContext
    ):
        for effect in result.effects:
            await self.effect_executor.execute(effect, chat)
        
        # 2. messages (+ ui)
        used_ui_targets = set()

        for msg in result.messages:
            target_id = self.effect_executor.resolve_audience(msg.target, chat,context)

            ui = next(
                (a for a in result.ui_actions if a.target == msg.target),
                None
            )

            if ui:
                used_ui_targets.add(ui.target)

            sent=await self.adapter.send_message(
                target_id,
                msg.text,
                ui_action=ui
            )
            if msg.intent and msg.intent.kind == "bindable":
                await self.effect_executor.binding_service.bind(
                    session=db_session,
                    platform="telegram",
                    session_id=chat.id,          # یا هر session_id درست
                    external_message_id=sent.message_id,  # ← این مهم‌ترین خط
                    
                )
            

        # 3. remaining ui actions (edit only)
        for action in result.ui_actions:
            if action.target not in used_ui_targets:
                target_id = self.effect_executor.resolve_audience(action.target, chat)
                await self.adapter.apply_ui(target_id, action)
        # for msg in result.messages:
        #     target_id = self.effect_executor.resolve_audience(msg.target, chat)
        #     await self.adapter.send_message(target_id, msg.text)

        # for action in result.ui_actions:
        #     target_id = self.effect_executor.resolve_audience(action.target, chat)
        #     await self.adapter.apply_ui(target_id, action)
         
class TelegramEffectExecutor:

    def __init__(self, adapter:TelegramAdapter, binding_service:telegram_binding_service.ReplyMessageBindingServiceImpl):
        self.adapter = adapter
        self.binding_service = binding_service
    async def execute(self, effect: Effect, chat: ChatSession):
        pass
        # match effect:

            # case SendAndBindMessage():
            #     target_id = self.resolve_audience(effect.audience, chat)

            #     msg = await self.adapter.send_message(
            #         target_id=target_id,
            #         text=effect.text
            #     )

            #     self.binding_service.bind(
            #         platform="telegram",
            #         session_id=effect.session_id,
            #         message_id=msg.message_id,
            #         target_id=target_id
            #     )

    def resolve_audience(self,audience: Audience, chat: ChatSession,context: RequestContext) -> int:
        match audience:
            case Audience.USER:
                return chat.external_user_id
            case Audience.SELLER:
                return chat.assigned_human_id or context.seller_id
