from fastapi import APIRouter

from .api.v1.router import router as v1_router

router=APIRouter()

@router.get("/health")
def health_cheack():
    return {
        "status":"ok"
    }

router.include_router(v1_router)    