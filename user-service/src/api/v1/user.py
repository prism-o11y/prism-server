from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.exceptions import HTTPException
from ...jwt.service import get_jwt_manager, JWTManager
from ...svc.user.service import UserService
from fastapi.responses import JSONResponse
from ...kafka.model import Action
from authlib.integrations.starlette_client import OAuthError
import logging, uuid, json, datetime as dt
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK
from ...svc.user.service import get_user_service
from ...svc.user.models import User

_router = APIRouter(prefix="/user")

@_router.get("/get-user-by-id", name="user:get-user-by-id")
async def get_user_by_id(payload:dict[str,str], user_svc:UserService = Depends(get_user_service)):
    user_id = payload.get("user_id")
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
async def get_user_by_email(payload:dict[str,str], user_svc:UserService = Depends(get_user_service)):
    email = payload.get("email")
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
@_router.get("/get-all-users", name="user:get-all-users")
async def get_all_users(user_svc:UserService = Depends(get_user_service)):
    try:

        users = await user_svc.get_all_users()
        if not users:
            return JSONResponse(
                status_code=HTTP_404_NOT_FOUND,
                content = {
                    "status":"Failed",
                    "message": "No users found",
                    "data": None
                }
            )
        
        rows_serialized =  [
                                {key: str(value) if isinstance(value, (uuid.UUID, dt.datetime)) else value for key, value in row.items()}  
                                for row in users
        ]
        
        return JSONResponse(
            status_code=HTTP_200_OK,
            content = {
                "status":"Success",
                "message": "Users found",
                "data": rows_serialized
            }
        )
    
    except Exception as e:
        logging.exception({"event": "Get-All-Users", "status": "Failed", "error": str(e)})
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
async def delete_user(request:Request,
                        user_svc:UserService = Depends(get_user_service),
                        jwt_manager:JWTManager = Depends(get_jwt_manager)):
    
    jwt = request.cookies.get("jwt")
    if not jwt:
        JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    is_valid, token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )
    
    user_id = token.get("user_id")
    data = {
        "user_id": user_id
    }

    await user_svc.produce_user_request(data, user_id, Action.DELETE_USER)

    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Waiting",
            "message": "Processing delete user request",
            "data": None
        }
    )