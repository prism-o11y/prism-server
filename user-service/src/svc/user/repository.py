from typing import Optional
from asyncpg import Connection
from src.svc.user.user_model import User
from src.database.postgres import get_db_connection

class UserRepository:

    def __init__(self):

        self.connection:Connection = get_db_connection()

    async def create_user(self, user:User)-> Optional[str]:

        async with self.connection.transaction():

            insert_query = '''
                            INSERT INTO users (user_id, email, status_id, created_at, updated_at)
                            VALUES ($1, $2, $3, $4, $5)
                            ON CONFLICT (email) DO NOTHING
                            RETURNING user_id;
                            '''

            query_result= await self.connection.fetchval(
                insert_query,
                str(user.id),
                user.email,
                user.status_id,
                user.created_at,
                user.updated_at,
            )

            return query_result

    async def get_user(self, user_id):

        pass

    async def get_user_by_email(self, email):

        pass

    async def update_user(self, user):

        pass

    async def delete_user(self, user_id):

        pass

    async def get_users(self):

        pass

async def get_user_repository() -> UserRepository:

    return UserRepository()