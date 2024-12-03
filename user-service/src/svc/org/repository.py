from asyncpg import Connection
from fastapi import Depends, HTTPException
from ..user.repository import UserRepository, get_user_repository
from ..user.models import User
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from .models import Org, Status
from asyncpg import UniqueViolationError
import logging
from ...database.postgres import get_db_connection

class OrgRepository:
    def __init__(self,connection, user_repo) -> None:
        self.connection:Connection = connection
        self.user_repo:UserRepository = user_repo

    async def create_org(self, org: Org, user_id:str) -> tuple[bool,str]:
        try:

            async with self.connection.transaction():     
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
        
        except UniqueViolationError as e:
            return False, "Org already exists"

        
        except Exception as e:
            return False, str(e)
        
        return True, "Org created successfully"

    async def remove_user_from_org(self, user_id:str):
        org_id = await self.user_repo.get_user_org(user_id)

        if org_id is None:
            logging.error({"event": "Remove-User-From-Org", "user_id": user_id, "status": "Failed", "error": "User doesn't belong to an organization"})
            return
        
        row_updated = await self.user_repo.remove_user_from_org(user_id)

        if row_updated == 0:
                logging.error({"event": "Remove-User-From-Org", "user_id": user_id, "status": "Failed", "error": "User not found"})
                return

        logging.info({"event": "Remove-User-From-Org", "user_id": user_id, "status": "Success"})
            

    async def get_org_by_id(self, org_id:str):
        async with self.connection.transaction():
            
            query = '''
                    SELECT org_id, name, status_id, created_at, updated_at
                    FROM organizations 
                    WHERE org_id = $1 and status_id = $2;
                    '''
            
            org = await self.connection.fetchrow(
                query, 
                org_id,
                Status.ACTIVE.value
            )

            return org

    async def get_org_by_name(self, name:str):
        async with self.connection.transaction():
            
            query = '''
                    SELECT org_id, name, status_id, created_at, updated_at
                    FROM organizations 
                    WHERE name = $1 and status_id = $2;
                    '''
            
            org = await self.connection.fetchrow(
                query, 
                name,
                Status.ACTIVE.value
            )
            return org

    async def delete_org(self, org_id:str) -> tuple[bool,str]:
        async with self.connection.transaction():
            
            query = '''
                    UPDATE organizations
                    SET status_id = $1
                    WHERE org_id = $2;
                    '''
            
            result = await self.connection.execute(
                query, 
                Status.REMOVED.value,
                org_id
            )

            row_updated = int(result.split()[-1])

            if row_updated == 0:
                return False, "Org not found"

            return True, "Org deleted successfully"

    async def remove_users_from_org(self, org_id:str) -> tuple[bool,str]:
        async with self.connection.transaction():
            
            query = '''
                    UPDATE users
                    SET org_id = NULL
                    WHERE org_id = $1;
                    '''
            
            result = await self.connection.execute(
                query, 
                org_id
            )

            row_updated = int(result.split()[-1])
            if row_updated == 0:
                return False, "Org not found"

            return True, "Users removed from org successfully"
    
    async def update_org(self):
        async with self.connection.transaction():
            pass

    async def get_all_orgs(self):
        async with self.connection.transaction():
            
            query = '''
                    SELECT org_id, name, status_id, created_at, updated_at
                    FROM organizations 
                    '''
            
            orgs = await self.connection.fetch(
                query
            )

            return orgs


    
async def get_org_repository(connection:Connection = Depends(get_db_connection), user_repo: UserRepository = Depends(get_user_repository)) -> OrgRepository:
    return OrgRepository(connection, user_repo)
