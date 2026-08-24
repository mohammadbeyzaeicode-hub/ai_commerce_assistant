from typing import Optional, List, Dict

from back.src.models.user import User
from back.src.infrastructure.database.repositories.sqlalchemy_base_repository import SqlAlchemyRepository


class UserService:
    def __init__(self, user_repo: SqlAlchemyRepository[User]):
        self.user_repo = user_repo

    async def get_user(self, user_id: int) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)

    async def list_users(self) -> List[User]:
        return await self.user_repo.get_all()

    async def create_user(self, data: Dict) -> User:
        # محل مناسب برای validation آینده (email, mobile, ...)
        return await self.user_repo.create(data)

    async def update_user(self, user_id: int, data: Dict) -> Optional[User]:
        return await self.user_repo.update(user_id, data)

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repo.delete(user_id)
