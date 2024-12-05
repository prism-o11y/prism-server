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
from ..apps.service import AppService
from ..apps.models import Application
from ..apps.repository import AppRepository
from ..sse.models import AlertSeverity, SSEClients
from ..sse.service import SSEService, get_sse_service

class OrgService:

    def __init__(self, postgres_manager:PostgresManager,kafka_producer:KafkaProducerService, sse_service: SSEService) -> None:
        self.postgres_manager:PostgresManager = postgres_manager
        self.kafka_producer:KafkaProducerService = kafka_producer
        self.sse_service:SSEService = sse_service
        self.base_config:BaseConfig = get_base_config()

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
        user_id = token.get("user_id")
        
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            org_repo = OrgRepository(connection, user_repo)

            user = await user_repo.get_user_by_id(user_id)
            if not user:
                await self.sse_service.process_sse_message(
                    message = "User not found",
                    connection_id =str(user_id),
                    client_id = str(user_id),
                    severity = AlertSeverity.Warning
                )
                return

            org_id = await user_repo.get_user_org(user_id)
            if org_id:
                await self.sse_service.process_sse_message(
                    message = "User already belongs to an organization",
                    connection_id = str(org_id),
                    client_id = str(user_id),
                    severity = AlertSeverity.Warning
                )
                return

            org_exist = await org_repo.get_org_by_name(name)
            if org_exist:
                org = Org(**dict(org_exist))
                await self.sse_service.process_sse_message(
                    message = "Org already exists",
                    connection_id = str(org.org_id),
                    client_id = str(user_id),
                    severity = AlertSeverity.Warning
                )
                return
            
            org:Org = await self.generate_org(name)

            org_created, org_msg = await org_repo.create_org(org, user_id)
            
            org_added, usr_msg = await user_repo.add_user_to_org(user_id, org.org_id)

            if org_created and org_added:
            
                await self.sse_service.process_sse_message(
                    message = org_msg + " & " + usr_msg,
                    connection_id = str(org.org_id),
                    client_id = str(user_id),
                    severity = AlertSeverity.Info
                ) 


    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def add_user_to_org(self, new_user_email:str, token: dict):
        admin_user_id = token.get("user_id")
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            org_id = await user_repo.get_user_org(admin_user_id)

            if not org_id:
                await self.sse_service.process_sse_message(
                    message = "Current user doesn't belong to an organization",
                    connection_id = str(admin_user_id),
                    client_id = str(admin_user_id),
                    severity = AlertSeverity.Warning
                )
                return
            
            user = await user_repo.get_user_by_email(new_user_email)
            if not user:
                await self.sse_service.process_sse_message(
                    message = "User doesn't exist",
                    connection_id = str(admin_user_id),
                    client_id = str(admin_user_id),
                    severity = AlertSeverity.Warning
                )
                return
            
            user = User(**dict(user))
            if user.org_id:
                await self.sse_service.process_sse_message(
                    message = "User already belongs to an organization",
                    connection_id = str(user.org_id),
                    client_id = str(admin_user_id),
                    severity = AlertSeverity.Warning
                )
                return
            
            added, msg = await user_repo.add_user_to_org(user.user_id, org_id)
            if added:
                await self.sse_service.process_sse_message(
                    message = msg,
                    connection_id = str(user.user_id),
                    client_id = str(admin_user_id),
                    severity = AlertSeverity.Info
                )
                return

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def remove_user_from_org(self, token: dict):
        user_id = token.get("user_id")

        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            org_id = await user_repo.get_user_org(user_id)
            if not org_id:
                await self.sse_service.process_sse_message(
                    message = "User doesn't belong to an organization",
                    connection_id = str(user_id),
                    client_id = str(user_id),
                    severity = AlertSeverity.Warning
                )
                return
            
            removed, msg = await user_repo.remove_user_from_org(user_id)

            if removed:            
                await self.sse_service.process_sse_message(
                    message = msg,
                    connection_id = str(user_id),
                    client_id = str(user_id),
                    severity = AlertSeverity.Info
                )


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
        

    async def get_all_orgs(self):
        
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            org_repo = OrgRepository(connection, user_repo)
            result = await org_repo.get_all_orgs()
            if not result:
                return None
            
            orgs = [Org(**dict(org)).model_dump() for org in result]

            return orgs
        
    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def delete_org(self, token: dict):
        user_id = token.get("user_id")        
        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            app_repo = AppRepository(connection)
            result = await user_repo.get_user_by_id(user_id)
            if not result:
                await self.sse_service.process_sse_message(
                    message = "User not found",
                    connection_id = str(user_id),
                    client_id = str(user_id),
                    severity = AlertSeverity.Warning
                )
                return

            user = User(**dict(result))
            if user.org_id is None:
                await self.sse_service.process_sse_message(
                    message = "User doesn't belong to an organization",
                    connection_id = str(user_id),
                    client_id = str(user_id),
                    severity = AlertSeverity.Warning
                )
                return
                
            org_repo = OrgRepository(connection, user_repo)
            deleted, delete_msg = await org_repo.delete_org(user.org_id)
            removed, remove_msg = await org_repo.remove_users_from_org(user.org_id)
            removed_apps, remove_apps_msg = await app_repo.delete_app_by_org_id(user.org_id)

            if deleted and removed and removed_apps:
                await self.sse_service.process_sse_message(
                    message = delete_msg + " & " + remove_msg + " & " + remove_apps_msg,
                    connection_id = str(user.org_id),
                    client_id = str(user_id),
                    severity = AlertSeverity.Info
                )
                return
    
    async def get_org_by_user_id(self, user_id:str):

        async with self.postgres_manager.get_connection() as connection:
            user_repo = UserRepository(connection)
            org_repo = OrgRepository(connection, user_repo)
            org_id = await user_repo.get_user_org(user_id)
            if not org_id:
                return None
            
            org = await org_repo.get_org_by_id(org_id)
            
            org = Org(**dict(org))
            return org.model_dump_json()

    async def update_org(self):
        pass

    async def generate_org(self,name:str):

        return Org.create_org(name)
        

    

async def get_org_service(
        postgres_manager: PostgresManager = Depends(get_postgres_manager),
        kafka_producer: KafkaProducerService = Depends(get_kafka_producer_service),
        sse_service: SSEService = Depends(get_sse_service)
    ) -> OrgService:
    return OrgService(postgres_manager, kafka_producer, sse_service)