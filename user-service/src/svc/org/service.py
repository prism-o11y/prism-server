from .repository import OrgRepository, get_org_repository
from fastapi import Depends
class OrgService:

    def __init__(self,org_repo) -> None:
        self.org_repo:OrgRepository = org_repo

    async def create_org(self, name: str):
        pass

    async def add_user_to_org(self):
        pass

    async def remove_user_from_org(self):
        pass

    async def get_org_by_id(self):
        pass

    async def get_org_by_name(self):
        pass

    async def delete_org(self):
        pass

    async def update_org(self):
        pass

async def get_org_service(org_repo:OrgRepository = Depends(get_org_repository)) -> OrgService:
    return OrgService(org_repo)