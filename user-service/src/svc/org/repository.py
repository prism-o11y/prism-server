from asyncpg import Connection
from fastapi import Depends
from ....src.database.postgres import get_db_connection

class OrgRepository:
    def __init__(self,connection):
        self.connection:Connection = connection

    async def create_org(self, name:str):
        async with self.connection.transaction():
            pass

    async def add_user_to_org(self):
        async with self.connection.transaction():
            pass

    async def remove_user_from_org(self):
        async with self.connection.transaction():
            pass

    async def get_org_by_id(self):
        async with self.connection.transaction():
            pass

    async def get_org_by_name(self):
        async with self.connection.transaction():
            pass

    async def delete_org(self):
        async with self.connection.transaction():
            pass
    
    async def update_org(self):
        async with self.connection.transaction():
            pass
    
async def get_org_repository(connection:Connection = Depends(get_db_connection)) -> OrgRepository:
    return OrgRepository(connection)