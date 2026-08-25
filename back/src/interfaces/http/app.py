from urllib.parse import urlsplit

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from back.src.core.settings import settings
from .router import router

app=FastAPI(
    title="AI Commerce Assistant API",
    version="1.0.0",
    description="HTTP API for AI Commerce Assistant",
)

mini_app_origin = ""
if settings.MINI_APP_URL:
    parsed_mini_app_url = urlsplit(settings.MINI_APP_URL)
    mini_app_origin = f"{parsed_mini_app_url.scheme}://{parsed_mini_app_url.netloc}"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin
        for origin in (
            mini_app_origin,
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        )
        if origin
    ],
    allow_origin_regex=r"https://[a-z0-9-]+\.trycloudflare\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)