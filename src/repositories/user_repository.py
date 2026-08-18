from models.user import User
from repositories.sqlalchemy_base_repository import SqlAlchemyRepository


class UserRepository(SqlAlchemyRepository[User]):
    def __init__(self, session):
        super().__init__(session, User)
