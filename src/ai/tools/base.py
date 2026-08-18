from typing import Any, Dict

from services.integrations.context import RequestContext

class BaseTool:
    name: str = ""
    description: str = ""
    arguments_schema: Dict[str, Any] = {}
    _service_provider = None
    def set_service_provider(self, provider):
        self._service_provider = provider

    async def __call__(self, **kwargs):
        raise NotImplementedError("Tool must implement __call__() method")
    def get_service(self):
        if not self._service_provider:
            raise RuntimeError(
                f"Service provider not set for tool '{self.name}'"
            )
        return self._service_provider()
    def set_context(self, context: RequestContext):
        self.context = context