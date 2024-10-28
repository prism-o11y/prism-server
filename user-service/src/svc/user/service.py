from src.svc.user.repository import get_user_repository, UserRepository
from ...kafka import model
from fastapi import Depends
from .models import User
import datetime as dt, uuid, logging

class UserService:

    def __init__(self, userRepo: UserRepository):
        
        self.userRepo = userRepo

    async def create_user(self, email: str):

        user = User(
            id = uuid.uuid4(),
            org_id = None,
            email = email,
            status_id = 1,
            created_at = dt.datetime.now(),
            updated_at = dt.datetime.now(),
            last_login = None
        )

        message = model.KafkaMessage(
            action = 'insert_user',
            data = user.model_dump()
        )

        return await self.userRepo.create_user(user)
    
    async def register_user_kafka(self, data: dict):

        try:

            user = User(**data)

            query_result = await self.userRepo.create_user(user)

            if query_result:
                logging.info(f"User created: {user.email}")

            else:
                logging.info(f"User already exists: {user.email}, user logged in.")

        except Exception as e:

            logging.exception(f"Failed to register user: {e}")
            
    
    async def get_login_dates(self, user_id: str, access_token: str):

        pass

async def get_user_service(userRepo: UserRepository = Depends(get_user_repository)) -> UserService:
    
    return UserService(userRepo)
