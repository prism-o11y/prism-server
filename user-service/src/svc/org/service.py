from .repository import OrgRepository, get_org_repository
from ..user.repository import UserRepository
from ...database.postgres import get_postgres_manager, PostgresManager
from .models import Org
from ...kafka.producer import KafkaProducerService, get_kafka_producer_service
from ...kafka import model
from fastapi import Depends
from ..user.models import User
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from ...config.base_config import get_base_config,BaseConfig


class OrgService:

    def __init__(self, postgres_manager:PostgresManager,kafka_producer) -> None:
        self.postgres_manager:PostgresManager = postgres_manager
        self.kafka_producer:KafkaProducerService = kafka_producer
        self.base_config:BaseConfig = get_base_config()
    
    async def produce_create_org(self, name:str, token:dict):

        data = model.Data(
            action= model.Action.INSERT_ORG,
            data = {
                "name": name,
                "token": token
            }
        ).model_dump_json().encode("utf-8")

        message = model.EventData(
            source = model.SourceType.USER_SERVICE,
            data = data,
            email = None,
            user_id = token.get("user_id")
        )

        try:

            await self.kafka_producer.enqueue_message(
                topic = self.base_config.KAFKA.TOPICS.get("user"),
                key = str(token.get("user_id")),
                value = message.model_dump_json().encode("utf-8")
            )
            
            logging.info({"event": "Produce-Message", "org": name, "status": "Produced"})

        except Exception as e:
            logging.error({"event": "Produce-Message", "org": name, "status": "Failed", "error": str(e)})


    async def produce_org_request(self, data:dict, user_id, action:str ,email:str = None):

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
    async def create_org(self, name: str, token: dict):
        org:Org = await self.generate_org(name)
        user_id = token.get("user_id")
        
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            org_repo = OrgRepository(connection, user_repo)
            await org_repo.create_org(org, user_id)


    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def add_user_to_org(self, new_user_email:str, token: dict):
        admin_user_id = token.get("user_id")
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            org_repo = OrgRepository(connection, user_repo)
            await org_repo.add_user_to_org(new_user_email,admin_user_id)

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def remove_user_from_org(self, token: dict):
        user_id = token.get("user_id")

        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            org_repo = OrgRepository(connection, user_repo)
            await org_repo.remove_user_from_org(user_id)


    async def get_org_by_id(self, org_id:str):
        
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            org_repo = OrgRepository(connection,user_repo)
            result = await org_repo.get_org_by_id(org_id)

            if not result:
                return None
            
            org = Org(**dict(result))
            return org.model_dump_json()

    async def get_org_by_name(self, org_name:str):
        
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            org_repo = OrgRepository(connection, user_repo)
            result = await org_repo.get_org_by_name(org_name)

            if not result:
                return None
            
            org = Org(**dict(result))
            return org.model_dump_json()
        
    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def delete_org(self, token: dict):
        user_id = token.get("user_id")        
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            result = await user_repo.get_user_by_id(user_id)
            if not result:
                logging.error({"event": "Delete-Org", "status": "Failed", "error": "User not found"})
                return

            user = User(**dict(result))
            if user.org_id is None:
                logging.error({"event": "Delete-Org", "status": "Failed", "error": "User does not belong to any org"})
                return
                
            org_repo = OrgRepository(connection, user_repo)
            await org_repo.delete_org(user.org_id)
            await org_repo.remove_user_from_org(user_id)

    async def update_org(self):
        pass

    async def generate_org(self,name:str):

        return Org.create_org(name)
        

    

async def get_org_service(
        postgres_manager: PostgresManager = Depends(get_postgres_manager),
        kafka_producer: KafkaProducerService = Depends(get_kafka_producer_service),
    ) -> OrgService:
    return OrgService(postgres_manager, kafka_producer)