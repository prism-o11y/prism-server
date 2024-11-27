from fastapi import APIRouter, Request, Depends
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_201_CREATED
from ...jwt.service import get_jwt_manager, JWTManager
from ...svc.org.service import OrgService, get_org_service
from fastapi.responses import JSONResponse
import json

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
            content={"message": "User not authenticated"}
        )
    
    is_valid,token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED, 
            content={"message": "User not authenticated"}
        )

    await org_service.create_org(payload.get("name"),token)

    return JSONResponse(
        status_code = HTTP_201_CREATED,
        content = {"message":"Org created"}
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
            content={"message": "User not authenticated"}
        )
    
    is_valid,token = await jwt_manager.validate_jwt(jwt)
    if not is_valid:
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED, 
            content={"message": "User not authenticated"}
        )
    
    await org_service.add_user_to_org(payload.get("email"),token)

    return JSONResponse(
        status_code = HTTP_201_CREATED,
        content = {"message":"User added to org"}
    )


@_router.delete("/remove-user-from-org", name="org:remove-user-from-org")
async def remove_user_from_org():
    pass

@_router.get("/get-org-by-id", name="org:get-org-by-id")
async def get_org_by_id():
    pass

@_router.get("/get-org-by-name", name="org:get-org-by-name")
async def get_org_by_name():
    pass

@_router.delete("/delete-org", name="org:delete-org")
async def delete_org():
    pass

@_router.post("/update-org", name="org:update-org")
async def update_org():
    pass
