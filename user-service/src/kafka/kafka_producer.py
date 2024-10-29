from aiokafka import AIOKafkaProducer
import json, logging, asyncio
from fastapi import Request

class ProducerManager:

    def __init__(self, broker):
        self.broker = broker
        self.producer = None

    async def init_producer(self):

        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.broker,
        )

        await self.producer.start()
        logging.info("Kafka producer initialized.")

    async def stop_producer(self):

        if self.producer:
            await self.producer.stop()
            logging.info("Kafka producer stopped.")

    async def send_message(self, topic, message:str):
        try:
            serialized_message = message.encode('utf-8')
            asyncio.wait_for(
                await self.producer.send_and_wait(topic=topic, value=serialized_message),
                timeout=10
            )
            logging.info(f"Message sent to topic {topic}, message: {serialized_message}")

        except asyncio.TimeoutError:
            logging.exception(f"Timeout occured while sending message to topic {topic}")
        
        except Exception as e:
            logging.exception(f"Failed to send message to topic {topic}: {e}")

async def get_producer_manager(request: Request) -> ProducerManager:

    return request.app.state.producer_manager
