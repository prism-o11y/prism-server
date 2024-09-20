from fastapi import APIRouter

_router = APIRouter(prefix="/auth")


@_router.get("/login")
async def login():
    return {"message": "Login!"}
