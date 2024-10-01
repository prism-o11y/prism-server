from src.svc.user.repository import get_user_repository, UserRepository
from fastapi import Depends, Request
from src.svc.user.user_model import User
import datetime as dt

class UserService:

    def __init__(self, userRepo: UserRepository) -> None:
        
        self.userRepo = userRepo

    async def register_user(self, email: str) -> tuple[str|None]:

        user = User(
            email=email,
            status_id=1,
            created_at=dt.datetime.now(dt.timezone.utc),
            updated_at=dt.datetime.now(dt.timezone.utc),
        )

        return self.userRepo.create_user(user)


async def get_user_service(userRepo: UserRepository = Depends(get_user_repository)) -> UserService:

    return UserService(userRepo)
