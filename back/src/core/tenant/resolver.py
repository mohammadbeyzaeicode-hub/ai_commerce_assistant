class TenantContext:
    def __init__(self, tenant_id: str, user_id: str, channel: str):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.channel = channel
