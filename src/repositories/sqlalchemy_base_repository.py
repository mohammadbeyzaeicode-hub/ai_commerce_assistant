from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session

T = TypeVar("T")


class SqlAlchemyRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> Optional[T]:
        return self.session.get(self.model, id)

    async def get_all(self) -> List[T]:
        return self.session.query(self.model).all()

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        self.session.delete(entity)
        self.session.commit()
        
    async def delete_by_id(self, entity_id: int) -> None:
        entity =await self.get_by_id(entity_id)
        if not entity:
            return
        self.session.delete(entity)
        self.session.commit()
    

    async def save(self, entity: T) -> T:
        """
        برای update یا create (unit of work ساده)
        """
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
    async def commit(self):
        self.session.commit()
    
    async def refresh(self,entity:T) -> T:
        self.session.refresh(entity)    