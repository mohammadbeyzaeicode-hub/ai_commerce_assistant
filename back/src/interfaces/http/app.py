from fastapi import FastAPI

from .router import router

app=FastAPI(
    title="AI Commerce Assistant API",
    version="1.0.0",
    description="HTTP API for AI Commerce Assistant",
)

app.include_router(router)