from src.svc.user.repository import get_user_repository, UserRepository
from fastapi import Depends
from .models import User
import datetime as dt, uuid

class UserService:

    def __init__(self, userRepo: UserRepository):
        
        self.userRepo = userRepo

    async def register_user(self, email: str):

        user = User(
            id = uuid.uuid4(),
            org_id = None,
            email = email,
            status_id = 1,
            created_at = dt.datetime.now(),
            updated_at = dt.datetime.now(),
            last_login = None
        )

        return await self.userRepo.create_user(user)
    
    async def get_login_dates(self, user_id: str, access_token: str):

        pass

async def get_user_service(userRepo: UserRepository = Depends(get_user_repository)) -> UserService:
    
    return UserService(userRepo)
