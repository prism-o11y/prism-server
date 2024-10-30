from src.svc.user.repository import get_user_repository, UserRepository
from ...kafka import model
from fastapi import Depends
from .models import User, STATUS
import datetime as dt, uuid, logging
from ...kafka.kafka_producer import ProducerManager, get_producer_manager
from ...kafka.kafka_producer_service import get_producer_service, KafkaProducerService


class UserService:

    def __init__(self, userRepo: UserRepository, producer_manager:ProducerManager, kafka_producer_service: KafkaProducerService):
        
        self.userRepo = userRepo
        self.producer_manager = producer_manager
        self.kafka_producer_service = kafka_producer_service

    async def create_user(self, email: str):

        user = User(
            id = uuid.uuid4(),
            org_id = None,
            email = email,
            status_id = STATUS.ACTIVE.value,
            created_at = dt.datetime.now(),
            updated_at = dt.datetime.now(),
            last_login = None
        )

        data = model.KafkaData(
            action = model.Action.INSERT_USER, 
            user_data = user.model_dump(),
        ).model_dump_json().encode('utf-8')

        message = model.EventData(
            source = model.SourceType.USER_SERVICE,
            data = data,
            email = user.email,
            user_id = user.id
        )

        await self.kafka_producer_service.send_message(model.Topic.USER, message)

    
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

async def get_user_service(
        userRepo: UserRepository = Depends(get_user_repository), 
        producer_manager:ProducerManager = Depends(get_producer_manager),
        kafka_producer_service: KafkaProducerService = Depends(get_producer_service)
    ) -> UserService:
    
    return UserService(userRepo, producer_manager, kafka_producer_service)
