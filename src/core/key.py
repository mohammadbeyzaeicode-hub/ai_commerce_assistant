from typing import NamedTuple


class SessionKey(NamedTuple):
    tenant_id: str   # shop_id
    user_id: str
    channel: str     # telegram | web | api

    def as_string(self) -> str:
        return f"{self.tenant_id}:{self.user_id}:{self.channel}"
