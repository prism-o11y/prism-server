from fastapi import APIRouter, Request, Depends
from src.svc.auth.service import get_auth0_manager
from src.svc.auth.service import Auth0Manager
from src.svc.user.service import UserService
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuthError
import logging
from src.svc.user.service import get_user_service
_router = APIRouter(prefix="/auth")


@_router.get("/login",name="auth:login")
async def login(request: Request, auth0Manager = Depends(get_auth0_manager)):

    return await auth0Manager.oauth.auth0.authorize_redirect(
        request,request.url_for("auth:callback")
    )

@_router.get("/callback", name="auth:callback")
async def callback(request: Request, auth0Manager:Auth0Manager = Depends(get_auth0_manager), userSvc:UserService = Depends(get_user_service)):

    try:

        token = await auth0Manager.oauth.auth0.authorize_access_token(request)

        mgmt_token = await auth0Manager.get_management_token()

        if mgmt_token is None:

            logging.exception("Failed to get management token: ")

            return JSONResponse(
                status_code=500,
                content={"detail": "Failed to get management token"}
            )

        jwt_token = token.get("id_token")    

        decode_token = await auth0Manager.get_decoded_token(jwt_token)

        if decode_token is None:

            logging.error("No token found")

            return RedirectResponse(request.url_for("auth:login"), status_code=303)
        
        email = decode_token.get("email")

        sub = decode_token.get("sub")

        try:
            await userSvc.register_user(email)

            return JSONResponse(status_code=201, content={"detail": "User registered"})
            
        except Exception as e:

            logging.error(f"Failed to insert user: {e}")

            return JSONResponse(status_code=500, content={"detail": f"Failed to insert user: {e}"})

    except OAuthError as e:

        logging.error(f"OAuth error occurred: {e.error}, description: {e.description}")

        return RedirectResponse(request.url_for("auth:login"), status_code=303)
    

    




