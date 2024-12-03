from ...kafka.producer import KafkaProducerService, get_kafka_producer_service
from ...config.base_config import BaseConfig, get_base_config
from ...database.postgres import PostgresManager, get_postgres_manager
from ...svc.user.repository import UserRepository
from ...svc.user.models import User
from ...svc.sse.models import SSEClients, AlertSeverity
from fastapi import Depends
from ...kafka import model
from .models import Application
from .repository import AppRepository
from ..sse.service import SSEService, get_sse_service
import logging, uuid
from tenacity import retry, stop_after_attempt, wait_exponential

class AppService:

    def __init__(self, postgres_manager:PostgresManager,kafka_producer, sse_service:SSEService) -> None:
        self.postgres_manager:PostgresManager = postgres_manager
        self.kafka_producer:KafkaProducerService = kafka_producer
        self.sse_service:SSEService = sse_service
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
                await self.sse_service.process_sse_message(
                    message = "User not found",
                    connection_id = user_id,
                    client_id = SSEClients.TEST_CLIENT,
                    severity = AlertSeverity.Critical
                )
                return
            

            user = User(**dict(result))

            if not user.org_id:
                await self.sse_service.process_sse_message(
                    message = "User not associated with any org",
                    connection_id = user_id,
                    client_id = SSEClients.TEST_CLIENT,
                    severity = AlertSeverity.Critical
                )
                return

            app_repo = AppRepository(connection)

            app = await app_repo.get_app_by_name_and_url(name, url)

            app_obj = Application(**dict(app)) if app else None
            if app_obj:
                await self.sse_service.process_sse_message(
                    message = "App already exists",
                    connection_id = app_obj.app_id,
                    client_id = SSEClients.TEST_CLIENT,
                    severity = AlertSeverity.Warning
                )
                return
  
            app = await self.generate_app(user.org_id, name, url)

            created, message = await app_repo.create_app(app)
            
            if created:
                await self.sse_service.process_sse_message(
                    message = message,
                    connection_id = app.app_id,
                    client_id = SSEClients.TEST_CLIENT,
                    severity = AlertSeverity.Info
                )

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def update_app(self, app_name: str, app_url: str, token: dict):
        user_id = token.get("user_id")

        async with self.postgres_manager.get_connection() as connection:
            
            app_repo = AppRepository(connection)
            app = await app_repo.get_app_by_user_id_and_url(user_id, app_url)
            if not app:
                await self.sse_service.process_sse_message(
                    message = "App not found",
                    connection_id = user_id,
                    client_id = SSEClients.TEST_CLIENT,
                    severity = AlertSeverity.Warning
                )
                return
            
            app = Application(**dict(app))
            app.app_name = app_name

            updated, message = await app_repo.update_app(app)

            if updated:
                await self.sse_service.process_sse_message(
                    message = message,
                    connection_id = app.app_id,
                    client_id = SSEClients.TEST_CLIENT,
                    severity = AlertSeverity.Info
                )

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def delete_app(self,token: dict, app_name:str, app_url:str):
        user_id = token.get("user_id")

        async with self.postgres_manager.get_connection() as connection:

            app_repo = AppRepository(connection)

            app = await app_repo.get_app_by_name_and_url(app_name, app_url)
            if not app:
                await self.sse_service.process_sse_message(
                    message = "App not found",
                    connection_id = user_id,
                    client_id = SSEClients.TEST_CLIENT,
                    severity = AlertSeverity.Warning
                )
                return
            
            app = Application(**dict(app))

            deleted, message = await app_repo.delete_app(app.app_id)

            if deleted:
                await self.sse_service.process_sse_message(
                    message = message,
                    connection_id = app.app_id,
                    client_id = SSEClients.TEST_CLIENT,
                    severity = AlertSeverity.Info
                )

    async def get_app_by_user_id(self, token:dict):
        user_id = token.get("user_id")

        async with self.postgres_manager.get_connection() as connection:

            app_repo = AppRepository(connection)
            result = await app_repo.get_app_by_user_id(user_id) 
            if not result:
                return None
            
            apps = [Application(**dict(app)).model_dump() for app in result]

            return apps
        
    async def get_app_by_user_id_and_url(self, token:dict, app_url:str):

        user_id = token.get("user_id")

        async with self.postgres_manager.get_connection() as connection:

            app_repo = AppRepository(connection)
            result = await app_repo.get_app_by_user_id_and_url(user_id, app_url)
            if not result:
                return None
            
            app = Application(**dict(result))

            return app.model_dump_json()
        

    async def get_app_by_id(self, app_id:uuid.UUID):

        async with self.postgres_manager.get_connection() as connection:

            app_repo = AppRepository(connection)
            result = await app_repo.get_app_by_id(app_id)
            if not result:
                return None
            
            app = Application(**dict(result))

            return app.model_dump_json()
        
    async def get_app_by_org_id(self, org_id:uuid.UUID):

        async with self.postgres_manager.get_connection() as connection:

            app_repo = AppRepository(connection)
            result = await app_repo.get_app_by_org_id(org_id)
            if not result:
                return None
            
            apps = [Application(**dict(app)).model_dump() for app in result]

            return apps
        
    async def get_all_apps(self):

        async with self.postgres_manager.get_connection() as connection:

            app_repo = AppRepository(connection)
            result = await app_repo.get_all_apps()
            if not result:
                return None
            
            apps = [Application(**dict(app)).model_dump() for app in result]

            return apps



    async def generate_app(self, org_id:uuid.UUID, name:str, url:str):
        return Application.create_application(org_id, name, url)

async def get_app_service(kafka_producer:KafkaProducerService = Depends(get_kafka_producer_service),
                          postgres_manager:PostgresManager = Depends(get_postgres_manager),
                          sse_service:SSEService = Depends(get_sse_service)):
    return AppService(postgres_manager=postgres_manager, kafka_producer=kafka_producer, sse_service=sse_service)