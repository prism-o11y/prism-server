from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from src.api.v1.entry import get_auth0_manager


_router = APIRouter(prefix="/auth")

@_router.get("/login")
async def login(request: Request):
    auth_manager = await get_auth0_manager(request)
    return RedirectResponse(auth_manager.auth0.auth0.authorize_redirect(request, redirect_uri=auth_manager.config.AUTH0_REDIRECT_URI))

@_router.get("/callback")
async def callback(request: Request):
    auth_manager = await get_auth0_manager(request)
    token = await auth_manager.auth0.auth0.authorize_access_token(request)
    user_info = await auth_manager.auth0.auth0.parse_id_token(request, token)

    # Step 3: Return the user info from Auth0
    return {"user_info": user_info}


