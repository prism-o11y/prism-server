from ...kafka.producer import KafkaProducerService, get_kafka_producer_service
from ...config.base_config import BaseConfig, get_base_config
from ...database.postgres import PostgresManager, get_postgres_manager
from ...svc.user.repository import UserRepository
from ...svc.user.models import User
from fastapi import Depends
from ...kafka import model
from .models import Application
from .repository import AppRepository
import logging, uuid
from tenacity import retry, stop_after_attempt, wait_exponential

class AppService:

    def __init__(self, postgres_manager:PostgresManager,kafka_producer) -> None:
        self.postgres_manager:PostgresManager = postgres_manager
        self.kafka_producer:KafkaProducerService = kafka_producer
        self.base_config:BaseConfig = get_base_config()

    async def produce_app_request(self, data:dict, user_id, action:str ,email:str = None):

        data = model.Data(
            action = action,
            data = data
        ).model_dump_json().encode("utf-8")

        message = model.EventData(
            source = model.SourceType.USER_SERVICE,
            data = data,
            email = email,
            user_id = user_id
        )

        try:

            await self.kafka_producer.enqueue_message(
                topic = self.base_config.KAFKA.TOPICS.get("user"),
                key = str(user_id),
                value = message.model_dump_json().encode("utf-8")
            )

            logging.info({"event": "Produce-Message", "action": action, "status": "Produced"})

        except Exception as e:
            logging.error({"event": "Produce-Message", "action": action, "status": "Failed", "error": str(e)})    

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def create_app(self, name:str, url:str, token:dict):
        user_id = token.get("user_id")
        
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            result = await user_repo.get_user_by_id(user_id)

            if not result:
                logging.error({"event": "Create-App", "status": "Failed", "error": "User not found"})
                return
            
            user = User(**dict(result))

            if not user.org_id:
                logging.error({"event": "Create-App", "status": "Failed", "error": "User not associated with any org"})
                return
            
            app = await self.generate_app(user.org_id, name, url)

            app_repo = AppRepository(connection)

            await app_repo.create_app(app)

    async def generate_app(self, org_id:uuid.UUID, name:str, url:str):
        return Application.create_application(org_id, name, url)

async def get_app_service(kafka_producer:KafkaProducerService = Depends(get_kafka_producer_service),
                          postgres_manager:PostgresManager = Depends(get_postgres_manager)):
    return AppService(postgres_manager=postgres_manager, kafka_producer=kafka_producer)