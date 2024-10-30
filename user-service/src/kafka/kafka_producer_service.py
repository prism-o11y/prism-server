from .kafka_producer import get_producer_manager, ProducerManager
from .model import KafkaData, EventData
from fastapi import Depends
import logging, tenacity, json

class KafkaProducerService:

    def __init__(self, producer_manager: ProducerManager):
        self.producer_manager = producer_manager

    @tenacity.retry(stop = tenacity.stop_after_attempt(3), wait = tenacity.wait_exponential(multiplier = 1, min = 4, max = 60))
    async def send_message(self, topic:str, message:EventData):

        try:
            logging.info(f"message: {json.dumps(message.model_dump_json())}")
            data: KafkaData = KafkaData.decode_data(message.data)
            serial_message = message.model_dump_json().encode('utf-8')

            await self.producer_manager.producer.send(
                topic = topic,
                value = serial_message
            )
            logging.info(f"Message sent to service: {message.source} with action: {data.action} for user: {message.user_id}")

        except Exception as e:
            logging.exception(f"Failed to send message to topic {topic}: {e}")



async def get_producer_service(producer_manager: ProducerManager = Depends(get_producer_manager)) -> KafkaProducerService:

    return KafkaProducerService(producer_manager)