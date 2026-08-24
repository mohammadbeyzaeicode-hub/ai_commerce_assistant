import asyncio
import json
import os
from back.src.ai.llm_client import LLMClient, AsyncLLMClient


import json

from back.src.ai.tools.Inventory_tools import CheckInventoryTool
from back.src.ai.tools.order_tools import CreateOrderTool
from back.src.ai.tools.product_tools import CreateProductTool
from back.src.core.key import SessionKey
from back.src.core.settings import settings
from back.src.models.Enum.enum import SenderType
from back.src.services import chat_log_service, order_service
from back.src.models.product.aplication.services import product_service
from back.src.services.integrations.context import RequestContext

class LLMOrchestrator:
    """
    Orchestrator دارای مدیریت داخلی session
    + انجام trimming خودکار تاریخچه
    """

    def __init__(
        self,
        api_key: str,
        session_backend,
        tools: dict,
        chat_log_service:chat_log_service.ChatLogService,
        context:RequestContext,
        sender_type:SenderType,        
        max_tokens_history: int = 3000,  # افزایش از 1000 به 3000
        
    ):
        """
        session_backend_cls: کلاسی که یک backend session می‌سازد
        max_tokens_history: سقف توکن‌های مجاز برای history trimming
        """
        self.llm = AsyncLLMClient(api_key=api_key,base_url=settings.GAPGPT_BASE_URL)
        self.session = session_backend()   # دیگر تزریق نمونهٔ ساخته‌شده نیست
        self.max_tokens_history = max_tokens_history
        self.sender_type=sender_type,
        self.chat_log_service=chat_log_service
        self.tools = tools
        for tool in self.tools.values():
            tool.set_context(context)
        


    # -------------------------------------------------------
    # history trimming برای جلوگیری از هزینه بالا
    # -------------------------------------------------------
    def trim_history(self, history):
        """
        history را از ابتدا کوتاه می‌کند تا حدود توکن مجاز.
        فرض: هر message حدوداً طبق یک تخمین lightweight اندازه‌گیری می‌شود.
        """

        def estimate_tokens(msg):
            base = 10

            content = msg.get("content")
            if content:
                base += len(content) // 4

            # اگر tool_calls وجود دارد، حدس بزنیم ~ 30 الی 50 توکن
            if msg.get("tool_calls"):
                base += 40

            return base
        total = 0
        trimmed = []

        # از آخر به اول می‌رویم، چون جدیدترین پیام‌ها مهم‌ترند
        for msg in reversed(history):
            t = estimate_tokens(msg)
            if total + t > self.max_tokens_history:
                break
            trimmed.append(msg)
            total += t

        # برعکس کردن مجدد برای ترتیب درست
        trimmed.reverse()
        print(f"Trimmed history: kept {len(trimmed)} messages (original: {len(history)}), estimated tokens: {total}")
        return trimmed

    # -------------------------------------------------------
    def build_messages(self, session_key: SessionKey):
        session_data = self.session.get_history(session_key)
        role = session_data.get("role", "buyer")
        history = session_data.get("messages", [])
        history = self.trim_history(history)

        prompt_path = (
            "src/ai/prompts/system_prompt_seller.txt"
            if role == "seller"
            else "src/ai/prompts/system_prompt_buyer.txt"
        )

        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
        else:
            system_prompt = (
                "You are a helpful assistant for buyers in an online store."
                if role == "buyer"
                else "You are a helpful assistant for the shop seller."
            )

        history = self.sanitize_messages(history)

        return [
            {"role": "system", "content": system_prompt},
            *history
        ]

    def sanitize_messages(self,messages):
        cleaned = []
        for msg in messages:
            # فقط پیام‌هایی را نگه دار که tool به‌درستی اجرا شده یا error نیستند
            if msg["role"] == "tool" and msg["content"].startswith("❌ Tool execution error"):
                msg["content"] = "❌Tool execution failed."
            cleaned.append(msg)
        return cleaned    
    def get_tools_for_role(self, role):
        common=["create_order","check_inventory","search_inventory","message_seller"]
        
        if role == "seller":
            allowed = [ "create_product","update_product"]
        else:
            allowed = []
        allowed.extend(common)
        print(allowed)
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.arguments_schema,
                }
            }
            for key, t in self.tools.items() if key in allowed
        ]
    import json


    
    async def run_tools(self, tool_calls: list[dict]):
        """
        Args:
            tool_calls : لیستی از objectهایی که مدل در پاسخ tool_call برگردانده
                         هر مورد شبیه {
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": "check_inventory",
                                "arguments": "{ \"product_id\": 123 }"
                            }
                         }
        Returns:
            list of tool_messages to append into messages context
        """
        tool_messages = []

        for call in tool_calls:
            try:
                func_name = call["function"]["name"]
                args_json = call["function"].get("arguments", "{}")
                args = json.loads(args_json)

                # بررسی وجود تابع در self.tools
                if func_name not in self.tools:
                    result = f"❌ Unknown tool '{func_name}'"
                else:
                    tool_func = self.tools[func_name]
                    if asyncio.iscoroutinefunction(tool_func.__call__):
                        result = await tool_func(**args)
                    else:
                        result = tool_func(**args)  # اجرای واقعی Tool

            except Exception as e:
                result = f"❌ Tool execution error: {str(e)}"

            # تلاش برای سریالایز کردن نتیجهٔ tool به صورت امن
            try:
                content = json.dumps(result, ensure_ascii=False)
            except TypeError:
                # تلاش برای استخراج dict یا تبدیل به رشته
                try:
                    if hasattr(result, "dict"):
                        content = json.dumps(result.dict(), ensure_ascii=False)
                    elif hasattr(result, "__dict__"):
                        content = json.dumps(result.__dict__, ensure_ascii=False)
                    else:
                        content = json.dumps(str(result), ensure_ascii=False)
                except Exception:
                    content = json.dumps(str(result), ensure_ascii=False)
            
            # اگر result بسیار بزرگ است، خلاصه کن تا payload بیش از حد بزرگ نشود
            if len(content) > 5000:
                print(f"Warning: Tool '{func_name}' result too large ({len(content)} bytes), truncating...")
                content = json.dumps(str(result)[:500] + "...", ensure_ascii=False)

            tool_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "name": func_name,
                    "content": content,
                }
            )

        return tool_messages

    # -------------------------------------------------------
    async def run(self, text: str, session_key: SessionKey,sender_type:SenderType):
        
        session_data = self.session.get_history(session_key)
        role = session_data.get("role")

        if role is None:
            role = self.resolve_role(session_key)
            self.session.set(
                session_key,
                {"role": role, "messages": []}
            )

        # 1) ثبت پیام کاربر
        self.session.append(session_key, "user", text)
        await self.chat_log_service.append_message(
            session_key=session_key,
            role="user",
            sender_type=sender_type.value,
            content=text,
        )
        # 2) ساخت context
        messages = self.build_messages(session_key)

        # 3) ابزارها
        tools = self.get_tools_for_role(role)
        print(self.llm.client.api_key)
        print(self.llm.client.base_url)
        print(self.llm.model)
        
        try:
            response = await self.llm.chat(
                messages=messages,
                tools=tools,
            )
        except Exception as e:
            # اگر فراخوانی اول ناموفق بود، پیام خطا بفرست
            print("First LLM call failed:", repr(e))
            print(f"Messages count: {len(messages)}, Payload size: {len(json.dumps(messages))} bytes")
            error_msg = "متأسفانه، در حال حاضر نمی‌توانم جواب دهم. لطفاً دوباره تلاش کنید."
            self.session.append(session_key, "assistant", error_msg)
            await self.chat_log_service.append_message(
                session_key=session_key,
                role="assistant",
                sender_type=SenderType.BOT.value,
                content=error_msg,
            )
            return error_msg

        message = response["choices"][0]["message"]

        # ------ Tool calls ------
        if message.get("tool_calls"):
            self.session.append(
                session_key,
                role="assistant",
                content="",
                tool_calls=message["tool_calls"],
            )
            await self.chat_log_service.append_message(
                session_key=session_key,
                role="assistant",
                sender_type=SenderType.BOT.value,
                content="",
                meta={"tool_calls": message["tool_calls"]},
            )

            tool_messages = await self.run_tools(message["tool_calls"])

            for tm in tool_messages:
                self.session.append(
                    session_key,
                    role="tool",
                    name=tm["name"],
                    tool_call_id=tm["tool_call_id"],
                    content=tm["content"],
                )
                
                await self.chat_log_service.append_message(
                    session_key=session_key,
                    role="tool",
                    sender_type=SenderType.SYSTEM.value,
                    content=tm["content"],
                    meta={
                        "tool": tm["name"],
                        "tool_call_id": tm["tool_call_id"],
                    },
)
            print(self.build_messages(session_key))
            # لاگ کوتاه از اندازهٔ پیام‌ها تا در صورت بروز خطا قابل بررسی باشد
            built = self.build_messages(session_key)
            final_msg = "متأسفانه، در حال پردازش پاسخ مشکلی پیش آمد. لطفاً دوباره تلاش کنید."
            
            try:
                print("Calling final LLM with messages:", len(built))
                final = await self.llm.chat(
                    messages=built,
                    tools=self.get_tools_for_role(role),
                )
                final_msg = final["choices"][0]["message"].get("content", "")
            except Exception as e:
                # لاگ کامل‌تر و فراخوانی مجدد یک‌بار برای خطاهای موقت
                print("LLM final call failed:", repr(e))
                try:
                    print("Retrying final LLM call...")
                    final = await self.llm.chat(
                        messages=built,
                        tools=self.get_tools_for_role(role),
                    )
                    final_msg = final["choices"][0]["message"].get("content", "")
                except Exception as e2:
                    print("LLM retry also failed:", repr(e2))
                    # fallback message - نه raise کردن exception
                    final_msg = "متأسفانه، در حال حاضر نمی‌توانم پاسخ دهم. لطفاً چند لحظه بعد تلاش کنید."
            
            self.session.append(session_key, "assistant", final_msg)
            await self.chat_log_service.append_message(
                session_key=session_key,
                role="assistant",
                sender_type=SenderType.BOT.value,
                content=final_msg,
            )
            return final_msg

        # ------ normal message ------
        assistant_msg = message.get("content", "")
        self.session.append(session_key, "assistant", assistant_msg)
        await self.chat_log_service.append_message(
            session_key=session_key,
            role="assistant",
            sender_type=SenderType.BOT.value,
            content=assistant_msg,
        )
        return assistant_msg
