from asyncpg.connection import Connection
import logging
from .models import Application
from ..sse.models import AlertSeverity
from asyncpg import UniqueViolationError
class AppRepository:

    def __init__(self, connection) -> None:
        self.connection:Connection = connection

    async def create_app(self, app:Application) -> tuple[bool, str]:

            
        async with self.connection.transaction():

            query = '''
                    INSERT INTO applications(app_id,org_id, app_name, app_url, created_at, updated_at)
                    VALUES($1,$2,$3,$4,$5,$6)
                    '''
            
            await self.connection.execute(
                query,
                app.app_id,
                app.org_id,
                app.app_name,
                app.app_url,
                app.created_at,
                app.updated_at,
            )
            
        return True, "App created successfully"

    
    async def update_app(self, app:Application) -> tuple[bool, str]:

        async with self.connection.transaction():

            query = '''
                    UPDATE applications
                    SET app_name = $1, updated_at = $2
                    WHERE app_id = $3
                    '''
            
            await self.connection.execute(
                query,
                app.app_name,
                app.updated_at,
                app.app_id,
            )

        return True, "App updated successfully"


    async def delete_app(self, app_id) -> tuple[bool, str]:

        async with self.connection.transaction():

            query = '''
                    DELETE FROM applications
                    WHERE app_id = $1
                    '''
            
            await self.connection.execute(
                query,
                app_id,
            )

        return True, "App deleted successfully"

    
    async def get_app_by_id(self, app_id):
            
            async with self.connection.transaction():
                query = '''
                        SELECT app_id, org_id, app_name, app_url, created_at, updated_at FROM applications
                        WHERE app_id = $1
                        '''
        
                result = await self.connection.fetchrow(
                    query,
                    app_id
                )
        
                return result
            
    async def get_app_by_user_id_and_url(self, user_id:str, app_url:str):

        async with self.connection.transaction():

            query = '''
                    SELECT app_id, org_id, app_name, app_url, created_at, updated_at 
                    FROM applications
                    WHERE org_id = (SELECT org_id FROM users WHERE user_id = $1) AND app_url = $2
                    '''
            
            result = await self.connection.fetchrow(
                query,
                user_id,
                app_url
            )

            return result
        
    async def get_app_by_user_id(self, user_id:str):

        async with self.connection.transaction():
            query = '''
                    SELECT app_id, org_id, app_name, app_url, created_at, updated_at FROM applications
                    WHERE org_id = (SELECT org_id FROM users WHERE user_id = $1)
                    '''
            
            result = await self.connection.fetch(
                query,
                user_id
            )

            return result
    
    async def get_app_by_org_id(self, org_id):

        async with self.connection.transaction():
            query = '''
                    SELECT app_id, org_id, app_name, app_url, created_at, updated_at FROM applications
                    WHERE org_id = $1
                    '''
            
            result = await self.connection.fetch(
                query,
                org_id
            )

            return result
        
    async def get_app_by_name_and_url(self, app_name:str, app_url:str):

        async with self.connection.transaction():
            query = '''
                    SELECT app_id, org_id, app_name, app_url, created_at, updated_at FROM applications
                    WHERE app_name = $1 AND app_url = $2
                    '''
            
            result = await self.connection.fetchrow(
                query,
                app_name,
                app_url
            )

            return result
        
    async def get_all_apps(self):

        async with self.connection.transaction():
            query = '''
                    SELECT app_id, org_id, app_name, app_url, created_at, updated_at FROM applications
                    '''
            
            result = await self.connection.fetch(query)

            return result
        

        
    