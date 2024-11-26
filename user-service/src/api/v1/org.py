from fastapi import APIRouter
from ...svc.org.models import Org
_router = APIRouter(prefix="/org")


@_router.post("/create-org", name="org:create-org")
async def create_org(name: str):
    pass

@_router.post("/add-user-to-org", name="org:add-user-to-org")
async def add_user_to_org():
    pass

@_router.post("/remove-user-from-org", name="org:remove-user-from-org")
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
