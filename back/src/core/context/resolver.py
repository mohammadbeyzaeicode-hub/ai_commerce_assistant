from .request_context import RequestContext

class ContextResolver:

    def __init__(
        self,
        store_channel_repo,
        store_repo,
    ):
        self.store_channel_repo = store_channel_repo
        self.store_repo = store_repo

    async def resolve(
        self,
        *,
        user_id: str,
        channel: str,
        channel_ref: str,
    ) -> RequestContext:

        store = self.store_channel_repo.get_by_channel_ref(
            channel=channel,
            channel_ref=channel_ref,
        )

        if not store:
            raise ValueError(
                f"Store not found for {channel=} {channel_ref=}"
            )

        seller_id = self.store_repo.get_seler_id(store.store_id)

        return RequestContext(
            user_id=user_id,
            store_id=store.store_id,
            seller_id=seller_id,
            channel=channel,
        )