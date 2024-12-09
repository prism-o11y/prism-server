from fastapi import APIRouter, Request, Depends
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR,HTTP_200_OK, HTTP_404_NOT_FOUND
from ...jwt.service import get_jwt_manager, JWTManager
from ...svc.org.service import OrgService, get_org_service
from fastapi.responses import JSONResponse
import json, logging, uuid, datetime as dt
from ...kafka.model import Action

_router = APIRouter(prefix="/org")


@_router.post("/create-org", name="org:create-org")
async def create_org(request:Request, 
                     payload:dict[str,str], 
                     jwt_manager: JWTManager = Depends(get_jwt_manager), 
                     org_service: OrgService = Depends(get_org_service)
    ):

    jwt = request.cookies.get("jwt")

    if not jwt:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    
    is_valid,token = await jwt_manager.validate_jwt(jwt)
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
        "name": payload.get("name"),
        "token": token
    }

    await org_service.produce_org_request(user_id=user_id, data=data, action=Action.INSERT_ORG)

    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message":"Processing org creation",
            "data": None
        }
    )

@_router.post("/add-user-to-org", name="org:add-user-to-org")
async def add_user_to_org(request:Request, 
                          payload:dict[str,str],
                          jwt_manager: JWTManager = Depends(get_jwt_manager), 
                          org_service: OrgService = Depends(get_org_service)
    ):

    jwt = request.cookies.get("jwt")

    if not jwt:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED, 
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )
    
    is_valid,token = await jwt_manager.validate_jwt(jwt)
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
        "email": payload.get("email"),
        "token": token
    }

    await org_service.produce_org_request(user_id=user_id, data=data, action = Action.ADD_USER_TO_ORG)

    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message":"Processing user addition",
            "data": None
        }
    )


@_router.delete("/remove-user-from-org", name="org:remove-user-from-org")
async def remove_user_from_org(request:Request,
                               jwt_manager: JWTManager = Depends(get_jwt_manager),
                               org_service: OrgService = Depends(get_org_service)
    ):

    jwt = request.cookies.get("jwt")

    if not jwt:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED, 
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    is_valid,token = await jwt_manager.validate_jwt(jwt)
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
        "token": token
    }

    await org_service.produce_org_request(user_id=user_id, data=data, action = Action.REMOVE_USER_FROM_ORG)

    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message":"Processing user removal",
            "data": None
        }
    )

@_router.delete("/delete-org", name="org:delete-org")
async def delete_org(request:Request,
                    jwt_manager: JWTManager = Depends(get_jwt_manager),
                    org_service: OrgService = Depends(get_org_service)
    ):
    
    jwt = request.cookies.get("jwt")

    if not jwt:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED, 
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )

    is_valid,token = await jwt_manager.validate_jwt(jwt)
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
        "token": token
    }

    await org_service.produce_org_request(user_id=user_id, data=data, action = Action.DELETE_ORG)

    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message":"Processing org deletion",
            "data": None
        }
    )

@_router.post("/update-org", name="org:update-org")
async def update_org():
    pass

@_router.get("/get-org-by-user-id", name="org:get-org-by-user-id")
async def get_org_by_user_id(request:Request,
                            jwt_manager: JWTManager = Depends(get_jwt_manager),
                            org_service: OrgService = Depends(get_org_service)
    ):

    jwt = request.cookies.get("jwt")
    if not jwt:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED, 
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )
    
    is_valid,token = await jwt_manager.validate_jwt(jwt)
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

    org = await org_service.get_org_by_user_id(user_id)

    if not org:
        return JSONResponse(
            status_code = HTTP_404_NOT_FOUND,
            content = {
                "status":"Failed",
                "message":"Organization not found",
                "data": None
            }
        )
    
    return JSONResponse(
        status_code = HTTP_200_OK,
        content = {
            "status":"Success",
            "message":"Organization found",
            "data": json.loads(org)
        }
    )
    

@_router.get("/get-org-by-id", name="org:get-org-by-id")
async def get_org_by_id(request:Request,
                        payload:dict[str,str],
                        jwt_manager: JWTManager = Depends(get_jwt_manager),
                        org_service: OrgService = Depends(get_org_service)
    ):
    
    jwt = request.cookies.get("jwt")

    if not jwt:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED, 
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )
    
    is_valid,token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED, 
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )
    try: 
        org_id = payload.get("org_id")

        org = await org_service.get_org_by_id(org_id)

        if not org:
            return JSONResponse(
                status_code = HTTP_404_NOT_FOUND,
                content = {
                    "status":"Failed",
                    "message":"Organization not found",
                    "data": None
                }
            )
        
        return JSONResponse(
            status_code = HTTP_200_OK,
            content = {
                "status":"Success",
                "message":"Organization found",
                "data": json.loads(org)
            }
        )
    
    except Exception as e:
        logging.exception({"event": "Get-Org-By-Id", "status": "Failed", "error": str(e)})
        return JSONResponse(
            status_code = HTTP_500_INTERNAL_SERVER_ERROR,
            content = {
                "status":"Failed",
                "message":"Internal server error",
                "data": None
            }
        )

@_router.get("/get-org-by-name", name="org:get-org-by-name")
async def get_org_by_name(request:Request,
                          payload:dict[str,str],
                          jwt_manager: JWTManager = Depends(get_jwt_manager),
                          org_service: OrgService = Depends(get_org_service)
    ):

    jwt = request.cookies.get("jwt")

    if not jwt:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED, 
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )
    
    is_valid,token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED, 
            content = {
                "status":"Failed",
                "message": "User not authenticated",
                "data": None
            }
        )
    
    try:
        org_name = payload.get("name")

        org = await org_service.get_org_by_name(org_name)

        if not org:
            return JSONResponse(
                status_code = HTTP_404_NOT_FOUND,
                content = {
                    "status":"Failed",
                    "message":"Organization not found",
                    "data": None
                }
            )
        
        return JSONResponse(
            status_code = HTTP_200_OK,
            content = {
                "status":"Success",
                "message":"Organization found",
                "data": json.loads(org)
            }
        )
    
    except Exception as e:
        logging.exception({"event": "Get-Org-By-Name", "status": "Failed", "error": str(e)})
        return JSONResponse(
            status_code = HTTP_500_INTERNAL_SERVER_ERROR,
            content = {
                "status":"Failed",
                "message":"Internal server error",
                "data": None
            }
        )
    

@_router.get("/get-all-orgs", name="org:get-all-orgs")
async def get_all_orgs(org_service: OrgService = Depends(get_org_service)):
    
    try:
        orgs = await org_service.get_all_orgs()

        if not orgs:
            return JSONResponse(
                status_code = HTTP_404_NOT_FOUND,
                content = {
                    "status":"Failed",
                    "message":"No organizations found",
                    "data": None
                }
            )
        
        org_serialized = [
            {key: str(value) if isinstance(value, (uuid.UUID, dt.datetime)) else value for key, value in row.items()}  
            for row in orgs
        ]
        
        return JSONResponse(
            status_code = HTTP_200_OK,
            content = {
                "status":"Success",
                "message":"Organizations found",
                "data": org_serialized
            }
        )
    
    except Exception as e:
        logging.exception({"event": "Get-All-Orgs", "status": "Failed", "error": str(e)})
        return JSONResponse(
            status_code = HTTP_500_INTERNAL_SERVER_ERROR,
            content = {
                "status":"Failed",
                "message":"Internal server error",
                "data": None
            }
        )
    

