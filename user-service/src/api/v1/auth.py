from fastapi import APIRouter, Request, Depends, HTTPException
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
    return await auth0Manager.oauth.auth0.authorize_redirect(
        request,request.url_for("auth:callback")
    )

@_router.get("/callback", name="auth:callback")
async def callback(request: Request, 
                    auth0_manager:Auth0Manager = Depends(get_auth0_manager), 
                    user_svc:UserService = Depends(get_user_service),
                    jwt_manager:JWTManager = Depends(get_jwt_manager)
    ):

    try:
        token = await auth0_manager.oauth.auth0.authorize_access_token(request)
        auth_token = token.get("id_token")
        if not auth_token:
            raise HTTPException(status_code=400, detail="Auth token not found")

        decoded_auth_token = await auth0_manager.get_decoded_token(auth_token)
        email = decoded_auth_token.get("email")

        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token")
        
        user:User = user_svc.generate_user(email)

        await user_svc.produce_new_user(user)

        return JSONResponse(status_code=201, content={"detail":"processing user login"})

    except HTTPException as e:
        logging.error(f"Auth error: {e.detail}")
        return RedirectResponse(url=request.url_for("auth:login"), status_code=303)

    except Exception as e:
        logging.exception("Unexpected error during authentication")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@_router.get("/logout", name="auth:logout")
async def logout(request: Request, auth0_manager: Auth0Manager = Depends(get_auth0_manager)):
    try:
        logout_url = auth0_manager.get_logout_url(request.url_for("auth:login"))
        return RedirectResponse(status_code = 303, url = logout_url)
    
    except Exception as e:
        logging.exception("Unexpected error during logout")
        return JSONResponse(status_code=500, content={"detail": "Internal server error during logout"})

    




