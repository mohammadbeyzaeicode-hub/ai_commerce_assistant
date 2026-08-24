from dataclasses import dataclass

@dataclass(frozen=True)
class RequestContext:
    user_id: str
    store_id: int
    seller_id: int | None
    channel: str