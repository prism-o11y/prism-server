from fastapi import APIRouter

_router = APIRouter(prefix="/auth")


@_router.get("/test")
def test():
    return {"message": "Hello World!"}
