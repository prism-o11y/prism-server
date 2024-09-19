from fastapi import APIRouter

_router = APIRouter()


@_router.get("/auth")
def test_route():
    return {"message": "Hello, world!"}
