from fastapi import APIRouter

from src.config.base_config import BaseConfig

_router = APIRouter(prefix="/auth")

@_router.get("/login")
async def login():
    return {"message": "Login!"}


