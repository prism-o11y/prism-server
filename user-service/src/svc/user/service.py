from src.svc.user.repository import get_user_repository, UserRepository
from ...kafka.producer import KafkaProducerService, get_kafka_producer_service
from ...kafka import model
from fastapi import Depends
from ...database.postgres import get_postgres_manager, PostgresManager
from .models import User, STATUS
import datetime as dt, uuid, logging
from ...config.base_config import get_base_config, BaseConfig
from tenacity import retry, stop_after_attempt, wait_exponential

class UserService:

    def __init__(self, postgres_manager: PostgresManager, kafka_producer: KafkaProducerService):
        self.kafka_producer = kafka_producer
        self.postgres_manager = postgres_manager
        self.base_config: BaseConfig = get_base_config()


    async def produce_new_user(self, email: str):

        user = User(
            id = uuid.uuid4(),
            org_id = None,
            email = email,
            status_id = STATUS.ACTIVE.value,
            created_at = dt.datetime.now(),
            updated_at = dt.datetime.now(),
            last_login = None
        )

        data = model.UserData(
            action = model.Action.INSERT_USER, 
            user_data = user.model_dump(),
        ).model_dump_json().encode('utf-8')

        message = model.EventData(
            source = model.SourceType.USER_SERVICE,
            data = data,
            email = user.email,
            user_id = user.id
        )

        try:
            await self.kafka_producer.enqueue_message(
                topic = self.base_config.KAFKA.TOPICS.get("user"),
                key = str(user.id),
                value = message.model_dump_json().encode('utf-8')
            )     

            logging.info({"event": "Produce-Message", "user": user.email, "status": "Produced"})

        except Exception as e:
            logging.error({"event": "Produce-Message", "user": user.email, "status": "Failed"})

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def insert_user(self, user: User):
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            result = await user_repo.create_user(user)

            if result:
                logging.info({"event": "User-Login", "user": user.email ,"status": "Signup-success"})

            else:
                
                logging.info({"event": "User-Login", "user": user.email ,"status": "Login-success"})

    


async def get_user_service(
        postgres_manager = Depends(get_postgres_manager),
        kafka_producer: KafkaProducerService = Depends(get_kafka_producer_service)
    ) -> UserService:
    
    return UserService(postgres_manager,kafka_producer)