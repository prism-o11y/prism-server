from src.svc.user.repository import get_user_repository, UserRepository
from ...kafka.producer import KafkaProducerService, get_kafka_producer_service
from ...kafka import model
from fastapi import Depends
from ...jwt.service import get_jwt_manager, JWTManager
from ...database.postgres import get_postgres_manager, PostgresManager
from .models import User, STATUS
import datetime as dt, uuid, logging
from ...config.base_config import get_base_config, BaseConfig
from tenacity import retry, stop_after_attempt, wait_exponential

class UserService:

    def __init__(self, postgres_manager: PostgresManager, kafka_producer: KafkaProducerService, jwt_manager: JWTManager) -> None:
        self.kafka_producer = kafka_producer
        self.postgres_manager = postgres_manager
        self.jwt_manager = jwt_manager
        self.base_config: BaseConfig = get_base_config()

    async def create_user(self, user:User, auth0_sub:str):
        result = await self.insert_user(user)
        jwt = await self.jwt_manager.encode(result, auth0_sub)
        return jwt

    async def produce_new_user(self, user: User):

        data = model.UserData(
            action = model.Action.INSERT_USER, 
            user_data = user.model_dump(),
        ).model_dump_json().encode('utf-8')

        message = model.EventData(
            source = model.SourceType.USER_SERVICE,
            data = data,
            email = user.email,
            user_id = user.user_id
        )

        try:
            await self.kafka_producer.enqueue_message(
                topic = self.base_config.KAFKA.TOPICS.get("user"),
                key = str(user.user_id),
                value = message.model_dump_json().encode('utf-8')
            )     

            logging.info({"event": "Produce-Message", "user": user.email, "status": "Produced"})

        except Exception as e:
            logging.error({"event": "Produce-Message", "user": user.email, "status": "Failed", "error": str(e)})

    async def produce_delete_user(self, user_id: uuid.UUID):

        data = model.UserData(
            action = model.Action.DELETE_USER,
            user_data = {"user_id": user_id}
        ).model_dump_json().encode('utf-8')

        message = model.EventData(
            source = model.SourceType.USER_SERVICE,
            data = data,
            email = None,
            user_id = user_id
        )

        try:
            await self.kafka_producer.enqueue_message(
                topic = self.base_config.KAFKA.TOPICS.get("user"),
                key = str(user_id),
                value = message.model_dump_json().encode('utf-8')
            )
            logging.info({"event": "Produce-Message", "user": user_id, "status": "Produced"})

        except Exception as e:
            logging.error({"event": "Produce-Message", "user": user_id, "status": "Failed", "error": str(e)})

    def generate_user(self, email:str) -> User:

        user = User(
            user_id = uuid.uuid4(),
            org_id = None,
            email = email,
            status_id = STATUS.ACTIVE.value,
            created_at = dt.datetime.now(),
            updated_at = dt.datetime.now(),
            last_login = None
        )

        return user



    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def insert_user(self, user: User) -> str:
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            result = await user_repo.create_user(user)
            return result

    async def get_user_by_id(self, user_id:uuid.UUID):

        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            result = await user_repo.get_user_by_id(user_id)
            if not result:
                return None
            
            else:
                user = User(**dict(result))
                return user.model_dump_json()
        
    async def get_user_by_email(self, email:str) -> str:

        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            result = await user_repo.get_user_by_email(email)

            if not result:
                return None
            
            else:
                user = User(**dict(result))
                return user.model_dump_json()
            
    async def update_user(self, user:User) -> str:

        async with self.postgres_manager.get_connection() as connection:

            user_repo = UserRepository(connection)

            result = await user_repo.update_user(user)

            if not result:
                return None
            
            else:

                return str(result)
            
    async def delete_user(self, user_id:uuid.UUID) -> str:

        async with self.postgres_manager.get_connection() as connection:

            user_repo = UserRepository(connection)

            result = await user_repo.delete_user(user_id)

            if not result:
                return None
            
            else:
                return str(result)
            
    async def get_all_users(self) -> list[User]:

        async with self.postgres_manager.get_connection() as connection:

            user_repo = UserRepository(connection)

            rows = await user_repo.get_all_users()

            if not rows:
                return None
            
            else:
                users = [User(**dict(user)).model_dump() for user in rows]
                return users


async def get_user_service(
        postgres_manager:PostgresManager = Depends(get_postgres_manager),
        kafka_producer: KafkaProducerService = Depends(get_kafka_producer_service),
        jwt_manager: JWTManager = Depends(get_jwt_manager)
    ) -> UserService:
    
    return UserService(postgres_manager,kafka_producer,jwt_manager)
