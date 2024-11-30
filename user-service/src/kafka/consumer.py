
import asyncio
import logging
from aiokafka import AIOKafkaConsumer
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config.kafka_config import KafkaConfig
from ..svc.user.service import UserService
from ..svc.org.service import OrgService
from ..svc.user.models import User
from ..svc.apps.service import AppService
from . import model

class KafkaConsumerService:
    def __init__(self, kafka_config: KafkaConfig, user_service: UserService, org_service: OrgService, app_service: AppService):
        self.broker = kafka_config.BROKER
        self.topic = kafka_config.TOPICS
        self.group_id = kafka_config.CONSUMER_GROUPS
        self.user_service = user_service
        self.org_service = org_service
        self.app_service = app_service
        self.user_consumer = None
        self.task = None

    @retry(wait = wait_exponential(multiplier = 1, min = 1, max = 10), stop = stop_after_attempt(10))
    async def start_user_consumer(self):

        self.user_consumer = AIOKafkaConsumer(
            self.topic.get("user"),
            bootstrap_servers = self.broker,
            group_id = self.group_id.get("user"),
            enable_auto_commit = False,
            auto_offset_reset = 'earliest',
        )

        await self.user_consumer.start()

        logging.info({"event": "Kafka-Consumer", "topic":self.topic.get('user'), "status": "Started"})

        self.task = asyncio.create_task(self._consume_messages())

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def stop_user_consumer(self):

        if self.task:
            self.task.cancel()
            try:
                await self.task

            except asyncio.CancelledError:
                logging.info({"event": "Kafka-Consumer", "topic":self.topic.get('user'), "status": "Cancelled"})

        await self.user_consumer.stop()
        logging.info({"event": "Kafka-Consumer", "topic":self.topic.get('user'), "status": "Stopped"})

    async def _consume_messages(self):
        try:
            async for message in self.user_consumer:
                await self.handle_message(message)

        except asyncio.CancelledError:
            logging.info({"event": "Kafka-Consumer", "topic":self.topic.get('user'), "status": "Cancelled"})

        except Exception as e:
            logging.exception({"event": "Kafka-Consumer", "topic":self.topic.get('user'), "status": e})
            raise

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
    async def handle_message(self, message):

        event_data = model.EventData.decode_message(message.value)
        logging.info({"event": "Consume-Message", "data": event_data.email, "status": "Received"})

        if event_data:
            await self.process_event(event_data)
            await self.user_consumer.commit()

        else:
            logging.error({"event": "Consume-Message", "data": event_data.email, "status": "Event Data Decode Failed"})

    async def process_event(self, event_data: model.EventData):

        if event_data.source == model.SourceType.USER_SERVICE:
            data = model.Data.decode_data(event_data.data)
            logging.info({"event": "Process-message", "action": data.action, "status": "Processing"})

            if data:
                match data.action:

                    case model.Action.INSERT_USER:
                        user = User(**data.data)
                        await self.user_service.insert_user(user)

                    case model.Action.UPDATE_USER:
                        pass

                    case model.Action.DELETE_USER:
                        await self.user_service.delete_user(user_id=data.data.get("user_id"))

                    case model.Action.INSERT_ORG:
                        await self.org_service.create_org(name = data.data.get("name"), token = data.data.get("token"))

                    case model.Action.UPDATE_ORG:
                        pass

                    case model.Action.DELETE_ORG:
                        await self.org_service.delete_org(token = data.data.get("token"))

                    case model.Action.ADD_USER_TO_ORG:
                        await self.org_service.add_user_to_org(new_user_email = data.data.get("email"), token = data.data.get("token"))

                    case model.Action.REMOVE_USER_FROM_ORG:
                        await self.org_service.remove_user_from_org(token = data.data.get("token"))

                    case model.Action.INSERT_APP:
                        await self.app_service.create_app(name = data.data.get("app_name"), url = data.data.get("app_url"), token = data.data.get("token"))

                    case _:
                        logging.warning({"event": "Process-message", "action": data.action, "status": "Unhandled"})
            else:
                logging.error({"event": "Process-message", "action": data.action, "status": "User Data Decode Failed"})
        else:
            logging.warning({"event": "Process-message", "source": data.source, "status": "Unhandled"})
