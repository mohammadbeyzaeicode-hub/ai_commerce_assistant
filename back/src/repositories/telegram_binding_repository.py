from back.src.models.telegram_reply import ReplyMessageBinding
from back.src.infrastructure.database.repositories.sqlalchemy_base_repository import SqlAlchemyRepository


class TelegramBindingRepository(SqlAlchemyRepository[ReplyMessageBinding]):
    def __init__(self, session):
        super().__init__(session, ReplyMessageBinding)
    
    async def get_by_external_message(
        self,
        *,
        platform: str,
        external_message_id: str,
    ) -> ReplyMessageBinding | None:
        return (
            self.session.query(ReplyMessageBinding)
            .filter_by(
                platform=platform,
                external_message_id=external_message_id,
            )
            .first()
        )

    async def create_or_update(
        self,
        *,
        message:ReplyMessageBinding
    ) -> None:
        obj = (
            self.session.query(ReplyMessageBinding)
            .filter_by(
                platform=message.platform,
                external_message_id=message.external_message_id,
            )
            .first()
        )

        if obj:
            obj.session_id = message.session_id
            obj.expires_at = message.expires_at
            saved_message=message
        else:
            saved_message=self.session.add(message )
        return  saved_message   
            
    async def cleanup_expired(self, *, now):
        return (
            self.session.query(ReplyMessageBinding)
            .filter(ReplyMessageBinding.expires_at < now)
            .delete()
        )    