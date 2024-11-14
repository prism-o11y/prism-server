from fastapi import APIRouter
from src.api.v1.auth import _router as auth_router
from src.api.v1.user import _router as user_router


def new_v1_router() -> APIRouter:
    router = APIRouter(prefix="/v1")
    router.include_router(auth_router)
    router.include_router(user_router)
    return router
