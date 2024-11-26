from typing import Optional
from asyncpg import Connection
from fastapi import Depends
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
                                            WHEN users.status_id = 2 THEN 1
                                            ELSE users.status_id
                                            END
                            RETURNING user_id;
                            '''

            query_result = await self.connection.fetchval(
                insert_query,
                user.user_id,
                user.email,
                user.status_id,
                user.created_at,
                user.updated_at,
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
                            SET status_id = 2
                            WHERE user_id = $1 AND status_id = $2
                            RETURNING user_id;
                           '''
            user_id = await self.connection.fetchval(
                select_query,
                user_id,
                STATUS.ACTIVE.value
            )

            return user_id
            

async def get_user_repository(connection:Connection = Depends(get_db_connection)) -> UserRepository:

    return UserRepository(connection)