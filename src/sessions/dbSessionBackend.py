# persistence/adapters/db_session_backend.py
import asyncio
from sessions.ports import ChatSessionPort

class DbSessionBackend(ChatSessionPort):

    def __init__(self, chat_log_service):
        self.chat_log = chat_log_service

    def append(self, session_key, role, content=None, **kwargs):
        return asyncio.run(
            self.chat_log.append_message(session_key, role, content, kwargs)
        )

    def get_history(self, session_key):
        messages = asyncio.run(
            self.chat_log.load_history(session_key)
        )
        return {
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    **(m.meta or {}),
                }
                for m in messages
            ]
        }

    def set(self, session_key, data):
        pass  # optional (role storage, metadata, etc)
