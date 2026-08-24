from typing import Protocol, Any, List, Optional

class AbstractRepository(Protocol):
    async def get_by_id(self, id: int) -> Optional[Any]:
        ...

    async def get_all(self) -> List[Any]:
        ...

    async def create(self, data: dict) -> Any:
        ...

    async def update(self, id: int, data: dict) -> Optional[Any]:
        ...

    async def delete(self, id: int) -> bool:
        ...
