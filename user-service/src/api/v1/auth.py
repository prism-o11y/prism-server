from fastapi import APIRouter, Request, Depends
from src.auth.auth0 import get_auth0_manager
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuthError
import logging
from src.user.user_model import User

_router = APIRouter(prefix="/auth")


@_router.get("/login",name="auth:login")
async def login(request: Request, auth0Manager = Depends(get_auth0_manager)):

    return await auth0Manager.oauth.auth0.authorize_redirect(
        request,request.url_for("auth:callback")
    )


@_router.get("/callback", name="auth:callback")
async def callback(request: Request, auth0Manager = Depends(get_auth0_manager)):

    try:
        token = await auth0Manager.oauth.auth0.authorize_access_token(request)

        id_token = token.get("id_token")

        decode_token = await auth0Manager.get_decoded_token(id_token)

        if decode_token is None:
            return RedirectResponse(request.url_for("auth:login"), status_code=303)
        
        user = User(
            email=decode_token.get("email"),
        )

        return {"user": user}

    except OAuthError as e:

        logging.error(f"OAuth error occurred: {e.error}, description: {e.description}")
        return RedirectResponse(request.url_for("auth:login"), status_code=303)

    




