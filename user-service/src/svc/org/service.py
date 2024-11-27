from .repository import OrgRepository, get_org_repository
from .models import Org
from fastapi import Depends
class OrgService:

    def __init__(self,org_repo) -> None:
        self.org_repo:OrgRepository = org_repo

    async def create_org(self, name: str, token: dict):
        org:Org = await self.generate_org(name)
        user_id = token.get("user_id")
        await self.org_repo.create_org(org,user_id)

    async def add_user_to_org(self, new_user_email:str, token: dict):
        
        admin_user_id = token.get("user_id")
        await self.org_repo.add_user_to_org(new_user_email,admin_user_id)

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

    async def generate_org(self,name:str):

        return Org.create_org(name)
        

    

async def get_org_service(org_repo:OrgRepository = Depends(get_org_repository)) -> OrgService:
    return OrgService(org_repo)