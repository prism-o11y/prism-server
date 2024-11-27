from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.exceptions import HTTPException
from ...jwt.service import get_jwt_manager, JWTManager
from ...svc.user.service import UserService
from fastapi.responses import JSONResponse
from authlib.integrations.starlette_client import OAuthError
import logging, uuid, json
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK
from ...svc.user.service import get_user_service
from ...svc.user.models import User
from ...kafka.model import EventData, SourceType, UserData, Action

_router = APIRouter(prefix="/user")

@_router.get("/get-user-by-id", name="user:get-user-by-id")
async def get_user_by_id(user_id:uuid.UUID, user_svc:UserService = Depends(get_user_service)):
    try:
        user = await user_svc.get_user_by_id(user_id)
        if not user:
            return JSONResponse(status_code=HTTP_404_NOT_FOUND, content={"detail": "User not found"})
        
        return JSONResponse(status_code=HTTP_200_OK, content=json.loads(user))
    
    except Exception as e:
        logging.exception({"event": "Get-User-By-Id", "status": "Failed", "error": str(e)})
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})
    
@_router.get("/get-user-by-email", name="user:get-user-by-email")
async def get_user_by_email(email:str, user_svc:UserService = Depends(get_user_service)):
    try:
        user = await user_svc.get_user_by_email(email)
        if not user:
            return JSONResponse(status_code=HTTP_404_NOT_FOUND, content={"detail": "User not found"})
        
        return JSONResponse(status_code=HTTP_200_OK, content=json.loads(user))
    
    except Exception as e:
        logging.exception({"event": "Get-User-By-Email", "status": "Failed", "error": str(e)})
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})
    
@_router.post("/update-user", name="user:update-user")
async def update_user(user:User, user_svc:UserService = Depends(get_user_service)):

    try:
        user_id = await user_svc.update_user(user)

        if not user_id:
            return JSONResponse(status_code=HTTP_404_NOT_FOUND, content={"detail": "User not found"})
        
        return JSONResponse(status_code=HTTP_200_OK, content={"user_id":user_id, "detail": "User updated successfully"})
    
    except Exception as e:
        logging.exception({"event": "Update-User", "status": "Failed", "error": str(e)})
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})
    
@_router.delete("/delete-user", name="user:delete-user")
async def delete_user(user_id:uuid.UUID, user_svc:UserService = Depends(get_user_service)):
    try:
        await user_svc.produce_delete_user(user_id)

        return JSONResponse(status_code=HTTP_200_OK, content={"detail": "User deletion request processing"})
    
    except Exception as e:
        logging.exception({"event": "Delete-User", "status": "Failed", "error": str(e)})
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})