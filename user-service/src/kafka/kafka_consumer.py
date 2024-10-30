from aiokafka import AIOKafkaConsumer
from ..svc.user.service import UserService
from ..svc.user.repository import UserRepository
from ..database.postgres import PostgresManager
from fastapi import Request
from .model import EventData
import asyncio, json, logging

class ConsumerManager:

    # def __init__(self, postgres_manager:PostgresManager, broker, topic, group_id):
    #     self.broker = broker
    #     self.topics = topic
    #     self.group_ids = group_id
    #     self.kafka_consumers = {}
    #     self.consumer_tasks = []
    #     self.action_handler = {
    #         'insert_user': self.insert_user,
    #         'update_user': None,
    #         'delete_user': None,
    #     }
    #     self.postgres_manager = postgres_manager
    #     self.repo = None
    #     self.user_svc = None

    def __init__(self, broker, topic, group_id):

        self.broker = broker
        self.topic = topic
        self.group_id = group_id

        self.user_consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.broker,
            group_id=self.group_id,
            enable_auto_commit=True,
            auto_offset_reset='earliest'
        )

        self.user_consumer_task = None

    async def init_kafka_consumer(self):

        await self.user_consumer.start()
        self.user_consumer_task = asyncio.create_task(self.consume_message(self.user_consumer, self.topic))

    async def consume_message(self, consumer, topic):

        async for msg in consumer:

            try:
                msg_value = msg.value.decode('utf-8')
                msg_data = json.loads(msg_value)
                msg_object = EventData(**msg_data)
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

        try:
            await self.user_svc.register_user_kafka(data)
            logging.info(f"{topic} - User registered: {data.get('email')}")

        except Exception as e:
            logging.exception(f"Failed to insert user: {e}")
        

    async def stop_kafka_consumers(self):
        for consumer in self.kafka_consumers.values():
            await consumer.commit()

            while True:

                messages = await consumer.poll(1.0)

                if not messages:
                    break

                for message in messages:
                    await self.process_message()
            await consumer.stop()

        for task in self.consumer_tasks:
            task.cancel()

            try:
                await task

            except asyncio.CancelledError:  
                pass

async def get_consumer_manager(request: Request) -> ConsumerManager:

    return request.app.state.consumer_manager

