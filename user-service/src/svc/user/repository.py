from typing import Optional
from asyncpg import Connection
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND
from fastapi import Depends, HTTPException
from src.svc.user.models import User, STATUS
import uuid
from src.database.postgres import PostgresManager, get_db_connection

from asyncpg import Connection
class UserRepository:

    def __init__(self, connection) -> None:

        self.connection:Connection = connection

    async def create_user(self, user:User)-> Optional[str]:

        async with self.connection.transaction():

            insert_query = '''
                            INSERT INTO users (user_id, email, status_id, created_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5)
                            ON CONFLICT (email) DO UPDATE
                            SET status_id = CASE
                                            WHEN users.status_id = $6 THEN $7
                                            ELSE users.status_id
                                            END,
                                updated_at = EXCLUDED.updated_at
                            RETURNING user_id;
                            '''

            query_result = await self.connection.fetchval(
                insert_query,
                user.user_id,
                user.email,
                user.status_id,
                user.created_at,
                user.updated_at,
                STATUS.REMOVED.value,
                STATUS.ACTIVE.value
            )

            return query_result

    async def get_user_by_id(self, user_id:uuid.UUID):

        async with self.connection.transaction():

            select_query = '''
                            SELECT user_id, org_id, email, status_id, created_at, updated_at, last_login
                            FROM users
                            WHERE user_id = $1 AND status_id = $2;
                            '''
            query_result = await self.connection.fetchrow(
                select_query,
                user_id,
                STATUS.ACTIVE.value
            )
            return query_result
        
    async def get_user_by_email(self, email:str):

        async with self.connection.transaction():

            select_query = '''
                            SELECT user_id, org_id, email, status_id, created_at, updated_at, last_login
                            FROM users
                            WHERE email = $1 AND status_id = $2;
                           '''
            query_result = await self.connection.fetchrow(
                select_query,
                email,
                STATUS.ACTIVE.value
            )
            return query_result
        
    async def update_user(self, user:User):

        async with self.connection.transaction():

            select_query = '''
                            UPDATE users
                            SET org_id = $1, updated_at = $2, last_login = $3
                            WHERE user_id = $4 AND status_id = $5
                            RETURNING user_id;
                           '''
            user_id = await self.connection.fetchval(
                select_query,
                user.org_id,
                user.updated_at,
                user.last_login,
                user.user_id,
                STATUS.ACTIVE.value
            )

            return user_id

    async def delete_user(self, user_id):

        async with self.connection.transaction():

            select_query = '''
                            UPDATE users
                            SET status_id = $1,
                                org_id = NULL
                            WHERE user_id = $2 AND status_id = $3
                            RETURNING user_id;
                           '''
            user_id = await self.connection.fetchval(
                select_query,
                STATUS.REMOVED.value,
                user_id,
                STATUS.ACTIVE.value
            )

            return user_id
        
    async def get_user_org(self, user_id: str) -> Optional[str]:

        async with self.connection.transaction():
            select_query = '''
                            SELECT org_id
                            FROM users
                            WHERE user_id = $1 AND status_id = $2;
                           '''
            org_id = await self.connection.fetchval(
                select_query,
                user_id,
                STATUS.ACTIVE.value
            )

            return org_id
        
    async def add_user_to_org(self, user_id:str, org_id:str):

        async with self.connection.transaction(): 
            user_org_insert_query = '''
                                    UPDATE users
                                    SET org_id = $1
                                    WHERE user_id = $2 and status_id = $3;
                                    '''

            result = await self.connection.execute(
                user_org_insert_query,
                org_id,
                user_id,
                STATUS.ACTIVE.value
            )

            row_updated = int(result.split()[-1])

            if row_updated == 0:
                raise HTTPException(
                    status_code = HTTP_404_NOT_FOUND,
                    detail = "User not found or error updating user"
                )
            

async def get_user_repository(connection:Connection = Depends(get_db_connection)) -> UserRepository:

    return UserRepository(connection)