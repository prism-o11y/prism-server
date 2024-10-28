from aiokafka import AIOKafkaConsumer
from ..svc.user.service import UserService
from ..svc.user.repository import UserRepository
from ..database.postgres import PostgresManager
from .model import KafkaMessage
import asyncio, json, logging

class ConsumerManager:

    def __init__(self, postgres_manager:PostgresManager):
        self.kafka_consumers = {}
        self.consumer_tasks = []
        self.action_handler = {
            'insert_user': self.insert_user,
            'update_user': None,
            'delete_user': None,
        }
        self.postgres_manager = postgres_manager
        self.repo = UserRepository(self.postgres_manager.get_connection())
        self.user_svc = UserService(self.repo)


    async def init_kafka_consumers(self, broker, topics, group_ids):

        for topic, group_id in zip(topics, group_ids):
            self.kafka_consumers[topic] = AIOKafkaConsumer(
                topic,
                bootstrap_servers = broker,
                group_id = group_id,
                enable_auto_commit = True,
                auto_offset_reset = 'earliest'
            )

            await self.kafka_consumers[topic].start()
            task = asyncio.create_task(self.consume_message(self.kafka_consumers[topic], topic))
            self.consumer_tasks.append(task)

    async def consume_message(self, consumer, topic):

        async for msg in consumer:

            try:
                msg_value = msg.value.decode('utf-8')
                msg_data = json.loads(msg_value)
                msg_object = KafkaMessage(**msg_data)
                await self.process_message(topic,msg_object.action, msg_object.data)

            except Exception as e:
                logging.exception(f"Error processing message from topic {topic}: {e}")
            
    async def process_message(self, topic, action, data):

        handler = self.action_handler.get(action)

        if handler:
            await handler(topic, data)

        else:
            raise Exception(f"No handler found for action {action} on topic {topic}")
        
    async def insert_user(self, topic, data):
        logging.info(f"{topic} - Attempting Inserting user: {data.get('email')}\n {data}")

        try:
            await self.user_svc.register_user_kafka(data)
            logging.info(f"{topic} - User registered: {data.get('email')}")

        except Exception as e:
            logging.exception(f"Failed to insert user: {e}")
        

    async def stop_kafka_consumers(self):
        for consumer in self.kafka_consumers.values():
            await consumer.stop()

        for task in self.consumer_tasks:
            task.cancel()

            try:
                await task

            except asyncio.CancelledError:  
                pass