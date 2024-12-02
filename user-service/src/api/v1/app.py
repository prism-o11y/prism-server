from fastapi import Depends, Request, Response, APIRouter
from ...jwt.service import JWTManager, get_jwt_manager
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from ...svc.apps.service import AppService, get_app_service
from ...kafka.model import Action
_router = APIRouter(prefix="/apps")

@_router.post("/add-application",name="app:add-application")
async def add_application(request:Request,
                            payload:dict[str,str],
                            jwt_manager: JWTManager = Depends(get_jwt_manager),
                            app_service: AppService = Depends(get_app_service)
    ):

    jwt = request.cookies.get("jwt")
    if not jwt:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    is_valid, token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    user_id = token.get("user_id")

    data = {
        "app_name": payload.get("app_name"),
        "app_url": payload.get("app_url"),
        "token": token
    }

    await app_service.produce_app_request(data, user_id, Action.INSERT_APP)


    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "Processing app creation",
            "data": None
        }
    )

@_router.post("/update-application",name="app:update-application")
async def update_application(request:Request,
                                payload:dict[str,str],
                                jwt_manager: JWTManager = Depends(get_jwt_manager),
                                app_service: AppService = Depends(get_app_service)
    ):

    jwt = request.cookies.get("jwt")
    if not jwt:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    is_valid, token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    user_id = token.get("user_id")

    data = {
        "app_name": payload.get("app_name"),
        "app_url": payload.get("app_url"),
        "token": token
    }

    await app_service.produce_app_request(data, user_id, Action.UPDATE_APP)


    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "Processing app update",
            "data": None
        }
    )

@_router.post("/delete-application",name="app:delete-application")
async def delete_application(request:Request,
                                payload:dict[str,str],
                                jwt_manager: JWTManager = Depends(get_jwt_manager),
                                app_service: AppService = Depends(get_app_service)
    ):

    jwt = request.cookies.get("jwt")
    if not jwt:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    is_valid, token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    user_id = token.get("user_id")

    data = {
        "app_name": payload.get("app_name"),
        "app_url": payload.get("app_url"),
        "token": token
    }

    await app_service.produce_app_request(data, user_id, Action.DELETE_APP)


    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "Processing app deletion",
            "data": None
        }
    )

@_router.get("/get-application",name="app:get-application")
async def get_application(request:Request,
                            payload:dict[str,str],
                            jwt_manager: JWTManager = Depends(get_jwt_manager),
                            app_service: AppService = Depends(get_app_service)
    ):

    jwt = request.cookies.get("jwt")
    if not jwt:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    is_valid, token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    user_id = token.get("user_id")

    data = {
        "app_name": payload.get("app_name"),
        "app_url": payload.get("app_url"),
        "token": token
    }


    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "Processing app retrieval",
            "data": None
        }
    )

@_router.get("/get-app-by-user-id",name="app:get-app-by-user-id")
async def get_app_by_user_id(request:Request,
                                jwt_manager: JWTManager = Depends(get_jwt_manager),
                                app_service: AppService = Depends(get_app_service)
    ):

    jwt = request.cookies.get("jwt")
    if not jwt:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    is_valid, token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    user_id = token.get("user_id")


    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "Processing app retrieval",
            "data": None
        }
    )

@_router.get("/get-app-by-org-id",name="app:get-app-by-org-id")
async def get_app_by_org_id(request:Request,
                                jwt_manager: JWTManager = Depends(get_jwt_manager),
                                app_service: AppService = Depends(get_app_service)
    ):

    jwt = request.cookies.get("jwt")
    if not jwt:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    is_valid, token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        JSONResponse(
            status_code = HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    user_id = token.get("user_id")


    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "Processing app retrieval",
            "data": None
        }
    )


