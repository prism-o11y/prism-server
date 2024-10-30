from aiokafka import AIOKafkaProducer
import json, logging, asyncio
from fastapi import Request

class ProducerManager:

    def __init__(self, broker):
        self.broker = broker
        self.producer = None

    async def init_producer(self):

        self.producer = AIOKafkaProducer(
            bootstrap_servers = self.broker,
        )

        await self.producer.start()
        logging.info("Kafka producer initialized.")

    async def stop_producer(self):
        if self.producer:
            await self.producer.stop()
            logging.info("Kafka producer stopped.")

async def get_producer_manager(request: Request) -> ProducerManager:
    return request.app.state.producer_manager
