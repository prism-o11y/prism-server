from asyncpg import Connection
from fastapi import Depends, HTTPException
from ..user.repository import UserRepository, get_user_repository
from ..user.models import User
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from .models import Org
from asyncpg import UniqueViolationError
import logging
from ...database.postgres import get_db_connection

class OrgRepository:
    def __init__(self,connection, user_repo) -> None:
        self.connection:Connection = connection
        self.user_repo:UserRepository = user_repo

    async def create_org(self, org: Org, user_id:str):

        org_id = await self.user_repo.get_user_org(user_id)

        if org_id is not None:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="User already belongs to an organization or user doesn't exist"
            )

        async with self.connection.transaction():
            
            try:
                org_insert_query = '''
                                    INSERT INTO organizations(org_id,name,status_id,created_at,updated_at)
                                    VALUES($1,$2,$3,$4,$5)
                                    RETURNING org_id;
                                    '''
                
                org_id = await self.connection.fetchval(
                    org_insert_query,
                    org.org_id,
                    org.name,
                    org.status_id,
                    org.created_at,
                    org.updated_at
                )
            
            except UniqueViolationError:

                raise HTTPException(
                    status_code=HTTP_409_CONFLICT,
                    detail="Organization already exists"
                )

            await self.user_repo.add_user_to_org(user_id, org_id)
            
    async def add_user_to_org(self, new_user_email:str, admin_user_id:str):

        org_id = await self.user_repo.get_user_org(admin_user_id)

        if org_id is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        query_user = await self.user_repo.get_user_by_email(new_user_email)
        logging.info(query_user)
        if query_user is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user = User(**dict(query_user))

        if user.org_id is not None:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="User already belongs to an organization"
            )
        
        await self.user_repo.add_user_to_org(user.user_id, org_id)


    async def remove_user_from_org(self):
        async with self.connection.transaction():
            pass

    async def get_org_by_id(self):
        async with self.connection.transaction():
            pass

    async def get_org_by_name(self, name:str):
        async with self.connection.transaction():
            pass

    async def delete_org(self):
        async with self.connection.transaction():
            pass
    
    async def update_org(self):
        async with self.connection.transaction():
            pass


    
async def get_org_repository(connection:Connection = Depends(get_db_connection), user_repo: UserRepository = Depends(get_user_repository)) -> OrgRepository:
    return OrgRepository(connection, user_repo)
