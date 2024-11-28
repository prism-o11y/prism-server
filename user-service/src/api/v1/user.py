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

_router = APIRouter(prefix="/user")

@_router.get("/get-user-by-id", name="user:get-user-by-id")
async def get_user_by_id(user_id:uuid.UUID, user_svc:UserService = Depends(get_user_service)):
    try:
        user = await user_svc.get_user_by_id(user_id)
        if not user:
            return JSONResponse(
                status_code=HTTP_404_NOT_FOUND,
                content = {
                    "status":"Failed",
                    "message": "User not found",
                    "data": None
                }
            )

        return JSONResponse(
            status_code=HTTP_200_OK,
            content = {
                "status":"Success",
                "message": "User found",
                "data": json.loads(user)
            }
        )
    
    except Exception as e:
        logging.exception({"event": "Get-User-By-Id", "status": "Failed", "error": str(e)})
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content = {
                "status":"Failed",
                "message": "Internal server error",
                "data": None
            }
        )
    
@_router.get("/get-user-by-email", name="user:get-user-by-email")
async def get_user_by_email(email:str, user_svc:UserService = Depends(get_user_service)):
    try:
        user = await user_svc.get_user_by_email(email)
        if not user:
            return JSONResponse(
                status_code=HTTP_404_NOT_FOUND,
                content = {
                    "status":"Failed",
                    "message": "User not found",
                    "data": None
                }
            )

        return JSONResponse(
            status_code=HTTP_200_OK,
            content = {
                "status":"Success",
                "message": "User found",
                "data": json.loads(user)
            }
        )
        
    
    except Exception as e:
        logging.exception({"event": "Get-User-By-Email", "status": "Failed", "error": str(e)})
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content = {
                "status":"Failed",
                "message": "Internal server error",
                "data": None
            }
        )
    
@_router.post("/update-user", name="user:update-user")
async def update_user(user:User, user_svc:UserService = Depends(get_user_service)):

    try:
        user_id = await user_svc.update_user(user)

        if not user_id:
            return JSONResponse(
                status_code=HTTP_404_NOT_FOUND,
                content = {
                    "status":"Failed",
                    "message": "User not found",
                    "data": None
                }
            )
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content = {
                "status":"Success",
                "detail": "User updated",
                "data": None
            }
        )
    
    except Exception as e:
        logging.exception({"event": "Update-User", "status": "Failed", "error": str(e)})
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content = {
                "status":"Failed",
                "message": "Internal server error",
                "data": None
            }
        )
    
@_router.delete("/delete-user", name="user:delete-user")
async def delete_user(user_id:uuid.UUID, user_svc:UserService = Depends(get_user_service)):
    try:
        await user_svc.produce_delete_user(user_id)

        return JSONResponse(
            status_code=HTTP_200_OK,
            content = {
                "status":"Success",
                "detail": "Processing delete user request",
                "data": None
            }
        )
    
    except Exception as e:
        logging.exception({"event": "Delete-User", "status": "Failed", "error": str(e)})
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content = {
                "status":"Failed",
                "message": "Internal server error",
                "data": None
            }
        )