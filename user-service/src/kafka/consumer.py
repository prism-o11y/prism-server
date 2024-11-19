
import asyncio
import logging
from aiokafka import AIOKafkaConsumer
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config.base_config import BaseConfig
from ..config.kafka_config import KafkaConfig
from ..svc.user.service import UserService
from ..svc.user.models import User
from . import model

class KafkaConsumerService:
    def __init__(self, kafka_config: KafkaConfig, user_service: UserService):
        self.broker = kafka_config.BROKER
        self.topic = kafka_config.TOPICS
        self.group_id = kafka_config.CONSUMER_GROUPS
        self.user_service = user_service
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
            user_data = model.UserData.decode_data(event_data.data)
            logging.info({"event": "Process-message", "action": user_data.action, "status": "Processing"})

            if user_data:
                match user_data.action:

                    case model.Action.INSERT_USER:
                        user = User(**user_data.user_data)
                        await self.user_service.insert_user(user)

                    case model.Action.UPDATE_USER:
                        pass

                    case model.Action.DELETE_USER:
                        pass

                    case _:
                        logging.warning({"event": "Process-message", "action": user_data.action, "status": "Unhandled"})
            else:
                logging.error({"event": "Process-message", "action": user_data.action, "status": "User Data Decode Failed"})
        else:
            logging.warning({"event": "Process-message", "source": event_data.source, "status": "Unhandled"})
