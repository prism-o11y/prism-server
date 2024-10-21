from src.svc.user.repository import get_user_repository, UserRepository
from fastapi import Depends
from src.svc.user.kafka_prod import UserProducer, get_user_producer
from src.svc.user.kafka_message_model import KafkaMessage
from src.svc.user.user_model import User
import datetime as dt, uuid

class UserService:

    def __init__(self, userRepo: UserRepository, userProducer: UserProducer):
        
        self.userRepo = userRepo

        self.userProducer = userProducer

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

        kafka_message = KafkaMessage(
            event="user.created",
            payload=user.model_dump(),
            timestamp=dt.datetime.now()
        )

        self.userProducer.produce("user-topic", kafka_message)

        # return await self.userRepo.create_user(user)
    
    async def get_login_dates(self, user_id: str, access_token: str):

        pass

async def get_user_service(userRepo: UserRepository = Depends(get_user_repository), 
                           userProd: UserProducer = Depends(get_user_producer)) -> UserService:
    
    return UserService(userRepo,userProd)
