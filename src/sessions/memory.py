from .base import SessionBackend


class InMemorySession(SessionBackend):
    def __init__(self):
        self.sessions = {}
    
    def get_history(self, chat_id: str):
        # اگه وجود نداره بسازش ولی بدون نقش پیش‌فرض
        if chat_id not in self.sessions:
            self.sessions[chat_id] = {"messages": [], "role": None}
        return self.sessions[chat_id]
    def append(
        self,
        chat_id: str,
        role: str,
        content=None,
        name: str = None,
        tool_calls=None,
        **kwargs
    ):
        # اگر چت هنوز ساخته نشده، مقدار اولیه برایش بساز
        if chat_id not in self.sessions:
            self.sessions[chat_id] = {
                "messages": [],
                "role": None
            }

        msg = {"role": role}

        if content is not None:
            msg["content"] = content

        if name:
            msg["name"] = name

        if tool_calls is not None:
            msg["tool_calls"] = tool_calls

        # سایر پارامترهای اضافی (اگر وجود دارد)
        msg.update(kwargs)

        # در لیست پیام‌ها اضافه کن
        self.sessions[chat_id]["messages"].append(msg)
