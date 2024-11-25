import asyncio, logging
from fastapi import Request
from aiokafka import AIOKafkaProducer
from ..config.base_config import get_base_config
from ..config.kafka_config import KafkaConfig
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import AsyncGenerator

class KafkaProducerService:
    def __init__(self, kafka_config: KafkaConfig, max_retries: int = 5, queue_max_size: int = 100):
        self.broker = kafka_config.BROKER
        self.producer = None
        self.queue = asyncio.Queue(maxsize=queue_max_size)
        self.max_retries = max_retries

    @retry(wait = wait_exponential(multiplier = 1, min = 1, max = 10), stop = stop_after_attempt(10))
    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.broker)
        await self.producer.start()
        logging.info({"event": "Kafka-Producer", "broker": self.broker, "status": "Connected"})
        asyncio.create_task(self._produce_messages())

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
    async def stop(self):
        await self.queue.join()
        await self.producer.stop()
        logging.info({"event": "Kafka-Producer", "broker": self.broker, "status": "Disconnected"})

    async def enqueue_message(self, topic: str, key: str, value: bytes):
        try:
            await asyncio.wait_for(self.queue.put((topic, key, value)), timeout=5)
        except asyncio.TimeoutError:
            logging.warning({"event": "MessageEnqueue", "topic": topic, "key": key, "status": "timeout"})

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10))
    async def _send_message_with_retry(self, topic: str, key: str, value: bytes):
        try:
            await self.producer.send_and_wait(topic, key=key.encode('utf-8'), value=value)

            logging.info({"event": "MessageSent", "topic": topic, "key": key, "status": "success"})
        except Exception as e:
            logging.exception({"event": "MessageSent", "topic": topic, "key": key, "status": "failed"})
            raise e

    async def _produce_messages(self):
        while True:
            topic, key, value = await self.queue.get()
            await self._send_message_with_retry(topic, key, value)
            self.queue.task_done()

async def get_kafka_producer_service(request: Request) -> AsyncGenerator[KafkaProducerService, None]:

    kafka_producer = request.app.state.kafka_producer
    yield kafka_producer