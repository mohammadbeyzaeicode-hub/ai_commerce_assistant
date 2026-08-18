import os
import json
from typing import Dict, Any

from core.settings import settings
from core.key import SessionKey


class JsonSessionBackend:
    """
    Backend برای ذخیرهٔ session در فایل JSON
    Session = Context موقت LLM
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sessions = self._load_all()

    # =====================
    # internal utils
    # =====================

    def _load_all(self) -> Dict[str, Any]:
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}

    def _save_all(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.sessions, f, ensure_ascii=False, indent=2)

    def _k(self, key: SessionKey) -> str:
        """normalize key"""
        return key.as_string()

    # =====================
    # public API
    # =====================

    def detect_role(self, key: SessionKey) -> str:
        """
        تشخیص نقش — موقت
        ⚠️ این منطق بعداً باید برود Service Layer
        """
        k = self._k(key)

        if k in self.sessions:
            role = self.sessions[k].get("role")
            if role is not None:
                return role

        if key.user_id in settings.SELLER_IDS:
            return "seller"

        return "buyer"

    def get_history(self, key: SessionKey) -> Dict[str, Any]:
        """
        خواندن history
        اگر session وجود نداشت → ساخته می‌شود
        """
        k = self._k(key)

        if k not in self.sessions:
            self.sessions[k] = {
                "messages": [],
                "role": self.detect_role(key),
            }
            self._save_all()

        return self.sessions[k]

    def save_history(self, key: SessionKey, data: Dict[str, Any]):
        k = self._k(key)
        self.sessions[k] = data
        self._save_all()

    def append(
        self,
        key: SessionKey,
        role: str,
        content=None,
        name: str | None = None,
        tool_calls=None,
        **kwargs,
    ):
        """
        افزودن پیام جدید — سازگار با:
        - tool_calls
        - content=None (برای tool message)
        """

        k = self._k(key)

        if k not in self.sessions:
            self.sessions[k] = {
                "messages": [],
                "role": self.detect_role(key),
            }

        msg = {"role": role}

        if content is not None:
            msg["content"] = content
        else :
             msg["content"] = ""
            

        if name:
            msg["name"] = name

        if tool_calls is not None:
            msg["tool_calls"] = tool_calls

        msg.update(kwargs)

        self.sessions[k]["messages"].append(msg)
        self._save_all()

    def clear(self, key: SessionKey):
        k = self._k(key)
        if k in self.sessions:
            del self.sessions[k]
            self._save_all()

    def set(self, key: SessionKey, data: dict):
        k = self._k(key)
        self.sessions[k] = data
        self._save_all()
