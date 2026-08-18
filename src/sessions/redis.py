import json
import redis
from .base import SessionBackend


class RedisSession(SessionBackend):
    def __init__(self, redis_url: str):
        self.r = redis.from_url(redis_url)

    def get_history(self, chat_id: str):
        raw = self.r.get(f"session:{chat_id}")
        if not raw:
            return []
        return json.loads(raw)

    def append(self, chat_id: str, role: str, content: str, name: str = None):
        history = self.get_history(chat_id)
        msg = {"role": role, "content": content}
        if name:
            msg["name"] = name
        history.append(msg)
        self.r.set(f"session:{chat_id}", json.dumps(history, ensure_ascii=False))
