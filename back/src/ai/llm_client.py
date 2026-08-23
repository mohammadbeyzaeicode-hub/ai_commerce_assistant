import asyncio
from typing import List, Dict, Any, Optional
from openai import OpenAI, AsyncOpenAI , InternalServerError, RateLimitError
from back.src.core.settings import settings

class LLMClient:
    """
    LLM Client — مسئول ارسال درخواست به مدل GPT-5.1
    فقط همین.
    هیچ منطقی از Orchestrator داخل آن نیست.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5.1",
        base_url: Optional[str] = None
    ):
        self.model = settings.model

        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url,timeout=100)
        else:
            self.client = OpenAI(api_key=api_key)

    def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        یک درخواست Cha tCompletion هم‌زمان (sync)
        """
        print("LLMClient.chat model:", self.model)
        print("GAPGPT_BASE_URL:", getattr(settings, "GAPGPT_BASE_URL", None))
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools
        )
        return response.model_dump()
        

class AsyncLLMClient:
    """
    نسخهٔ Async — مخصوص پروژه‌هایی که از FastAPI async استفاده می‌کنند
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5.1",
        base_url: Optional[str] = None
    ):
        self.model = settings.model
        
        if base_url:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = AsyncOpenAI(api_key=api_key)

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        نسخهٔ Async
        """
        
        retries = 3
        retries = 4

        for attempt in range(retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools
                )
                return response.model_dump()

            except (InternalServerError, RateLimitError) as e:
                print(f"LLM call attempt {attempt+1} failed with recoverable error: {repr(e)}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                # لاگ خطاهای غیرمنتظره و تلاش مجدد یک‌بار
                print(f"LLM call attempt {attempt+1} unexpected error: {repr(e)}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(1)
    