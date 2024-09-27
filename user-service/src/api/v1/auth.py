from fastapi import APIRouter, Request, Depends
from src.auth.auth0 import get_auth0_manager
from fastapi.responses import RedirectResponse
_router = APIRouter(prefix="/auth")


@_router.get("/login",name="auth:login")
async def login(request: Request, auth0Manager = Depends(get_auth0_manager)):

    return await auth0Manager.oauth.auth0.authorize_redirect(
        request,request.url_for("auth:callback")
    )


@_router.get("/callback", name="auth:callback")
async def callback(request: Request, auth0Manager = Depends(get_auth0_manager)):

    token = await auth0Manager.oauth.auth0.authorize_access_token(request)

    return {"message":token.get("email")}