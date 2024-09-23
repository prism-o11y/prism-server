from fastapi import APIRouter
from src.api.v1.auth import _router


def new_v1_router() -> APIRouter:
    router = APIRouter(prefix="/v1")
    router.include_router(_router)
    return router
