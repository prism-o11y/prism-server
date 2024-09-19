from fastapi import APIRouter
from src.api.v1.auth import _router as auth_router


def new_v1_router() -> APIRouter:
    router = APIRouter(prefix="/v1")
    router.include_router(auth_router)
    return router
