from fastapi import Depends, Request, Response, APIRouter
from ...jwt.service import JWTManager, get_jwt_manager
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from ...svc.apps.service import AppService, get_app_service
from ...kafka.model import Action
import json, uuid, datetime as dt
_router = APIRouter(prefix="/apps")

@_router.post("/add-app",name="app:add-app")
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

    await app_service.produce_app_request(data, user_id,Action.INSERT_APP)


    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "Processing app creation",
            "data": None
        }
    )

@_router.post("/update-app",name="app:update-app")
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

    await app_service.produce_app_request(data, user_id,Action.UPDATE_APP)


    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "Processing app update",
            "data": None
        }
    )

@_router.delete("/delete-app",name="app:delete-app")
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

    await app_service.produce_app_request(data, user_id,Action.DELETE_APP)


    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "Processing app deletion",
            "data": None
        }
    )

@_router.get("/get-app-by-id",name="app:get-app-by-id")
async def get_app_by_id(request:Request,
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

    app_id = payload.get("app_id")

    app = await app_service.get_app_by_id(app_id)
    if not app:
        return JSONResponse(
            status_code = HTTP_404_NOT_FOUND,
            content = {
                "status":"Failed",
                "message": "App not found",
                "data": None
            }
        )
    
    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "App found",
            "data": json.loads(app)
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

    apps = await app_service.get_app_by_user_id(token)


    if not apps:
        return JSONResponse(
            status_code = HTTP_404_NOT_FOUND,
            content = {
                "status":"Failed",
                "message": "App not found",
                "data": None
            }
        )
    apps_serialized = [
            {key: str(value) if isinstance(value, (uuid.UUID, dt.datetime)) else value for key, value in row.items()}  
            for row in apps
    ]
    
    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "App found",
            "data": apps_serialized
        }
    )

@_router.get("/get-app-by-user-id-and-url",name="app:get-app-by-user-id-and-url")
async def get_app_by_user_id_and_url(request:Request,
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

    app_url = payload.get("app_url")

    app = await app_service.get_app_by_user_id_and_url(token, app_url)
    if not app:
        return JSONResponse(
            status_code = HTTP_404_NOT_FOUND,
            content = {
                "status":"Failed",
                "message": "App not found",
                "data": None
            }
        )
    
    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "App found",
            "data": json.loads(app)
        }
    )

@_router.get("/get-app-by-org-id",name="app:get-app-by-org-id")
async def get_app_by_org_id(request:Request,
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

    org_id = payload.get("org_id")

    apps = await app_service.get_app_by_org_id(org_id)
    if not apps:
        return JSONResponse(
            status_code = HTTP_404_NOT_FOUND,
            content = {
                "status":"Failed",
                "message": "App not found",
                "data": None
            }
        )
    
    apps_serialized = [
            {key: str(value) if isinstance(value, (uuid.UUID, dt.datetime)) else value for key, value in row.items()}  
            for row in apps
    ]

    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "App found",
            "data": apps_serialized
        }
    )

@_router.get("/get-all-apps",name="app:get-all-apps")
async def get_all_apps(request:Request,
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

    apps = await app_service.get_all_apps()
    if not apps:
        return JSONResponse(
            status_code = HTTP_404_NOT_FOUND,
            content = {
                "status":"Failed",
                "message": "Apps not found",
                "data": None
            }
        )
    
    apps_serialized = [
            {key: str(value) if isinstance(value, (uuid.UUID, dt.datetime)) else value for key, value in row.items()}  
            for row in apps
    ]
    
    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message": "Apps found",
            "data": apps_serialized
        }
    )

