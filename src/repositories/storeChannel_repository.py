from models.store_channel import StoreChannel
from models.user import User
from repositories.sqlalchemy_base_repository import SqlAlchemyRepository


class StoreChannel_repository(SqlAlchemyRepository[StoreChannel]):
    def __init__(self, session):
        super().__init__(session, StoreChannel)
    def get_by_channel_ref(
        self,
        channel: str,
        channel_ref: str
    ) -> StoreChannel | None:
        return (
            self.session.query(StoreChannel)
            .filter(
                StoreChannel.channel == channel,
                StoreChannel.channel_ref == channel_ref
            )
            .one_or_none()
        )
