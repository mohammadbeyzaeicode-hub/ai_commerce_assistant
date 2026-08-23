from back.src.repositories.storeChannel_repository import StoreChannel_repository


class TenantResolver:
    def __init__(self, store_channel_repo: StoreChannel_repository):
        self.repo = store_channel_repo

    async def resolve(self, channel: str, channel_ref: str) -> int:
        store_channel = self.repo.get_by_channel_ref(
            channel=channel,
            channel_ref=channel_ref
        )
        if not store_channel:
            raise ValueError(
                f"Store not found for {channel=} {channel_ref=}"
            )
        return store_channel.store_id
    
    