from fastapi import APIRouter, Request, Depends, HTTPException, Response
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_303_SEE_OTHER
from fastapi.exceptions import HTTPException
from ...svc.auth.service import get_auth0_manager
from ...jwt.service import get_jwt_manager, JWTManager
from ...svc.auth.service import Auth0Manager
from ...svc.user.service import UserService
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuthError
import logging
from ...svc.user.service import get_user_service
from ...svc.user.models import User
_router = APIRouter(prefix="/auth")


@_router.get("/login",name="auth:login")
async def login(request: Request, auth0Manager = Depends(get_auth0_manager)):
    callback_url = f"{request.url.scheme}://{request.url.hostname}:81/api/user-service" + request.url_for("auth:callback").path
    return await auth0Manager.oauth.auth0.authorize_redirect(
        request,callback_url
    )

@_router.get("/callback", name="auth:callback")
async def callback(request: Request, 
                   response: Response,
                    auth0_manager:Auth0Manager = Depends(get_auth0_manager), 
                    user_svc:UserService = Depends(get_user_service),
                    jwt_manager:JWTManager = Depends(get_jwt_manager)
    ):

    try:
        token = await auth0_manager.oauth.auth0.authorize_access_token(request)
        auth_token = token.get("id_token")

        if not auth_token:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Auth token is missing")

        decoded_auth_token = await auth0_manager.get_decoded_token(auth_token)
        email = decoded_auth_token.get("email")
        sub = decoded_auth_token.get("sub")

        if not email:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Email not found in token")
        
        user:User = user_svc.generate_user(email)
        jwt = await user_svc.create_user(user, sub)

        response = RedirectResponse(url="http://localhost:3000")
        response.set_cookie(
            key="jwt",
            value=jwt,
            expires=60*60*24,
        )

        return response
    


    except HTTPException as e:
        logging.error(f"Auth error: {e.detail}")
        return RedirectResponse(url=request.url_for("auth:login"), status_code=HTTP_303_SEE_OTHER)

    except Exception as e:
        logging.exception("Unexpected error during authentication")
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})

@_router.get("/logout", name="auth:logout")
async def logout(request: Request, auth0_manager: Auth0Manager = Depends(get_auth0_manager)):
    try:
        logout_url = auth0_manager.get_logout_url(request.url_for("auth:login"))
        return RedirectResponse(status_code = HTTP_500_INTERNAL_SERVER_ERROR, url = logout_url)
    
    except Exception as e:
        logging.exception("Unexpected error during logout")
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error during logout"})

    




