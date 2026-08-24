from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: int
    is_active: bool
    store_id: int
    inventory: int

    model_config = ConfigDict(from_attributes=True)
    