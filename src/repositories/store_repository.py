from models.store import Store
from models.user import User
from repositories.sqlalchemy_base_repository import SqlAlchemyRepository


class StoreRepository(SqlAlchemyRepository[Store]):
    def __init__(self, session):
        super().__init__(session, Store)
    
    def get_seler_id(self,storeId:int):
        store=  self.session.query(Store).filter( Store.id == storeId) .one_or_none()
        return store.owner_id
        
            
