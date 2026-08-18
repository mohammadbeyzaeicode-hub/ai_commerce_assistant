# transport/context.py

from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class RequestContext:
    tenant_id: int
    user_id: int
    channel: str
    seller_id: Optional[int] = None
    store_id: Optional[int] = None
   