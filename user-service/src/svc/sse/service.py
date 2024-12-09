from .models import SSENotification,NotificationWrapper, Action
from ...kafka.producer import KafkaProducerService, get_kafka_producer_service
from fastapi import Depends
from ...config.base_config import BaseConfig, get_base_config
import datetime as dt, logging
class SSEService:

    def __init__(self, kafka_producer:KafkaProducerService):
        self.kafka_producer = kafka_producer
        self.base_config: BaseConfig = get_base_config()

    async def process_sse_message(self, message:str, client_id:str, severity:str, connection_id:str):
        try:
            
            sse_notification = SSENotification(
                client_id = client_id,
                connection_id = client_id,
                severity = severity,
                message = message,
                datetime = dt.datetime.now(dt.timezone.utc),
            ).model_dump()

            notifWrapper = NotificationWrapper(
                action = Action.SSE,
                data = sse_notification
            ).model_dump_json().encode('utf-8')

            await self.kafka_producer.enqueue_message(
                topic = self.base_config.KAFKA.TOPICS.get("notify"),
                key = client_id,
                value = notifWrapper
            )

            logging.info({"event": "Produce-SSE","status": "Success"})

        except Exception as e:

            logging.error({"event": "Produce-SSE","status": "Failed", "error": str(e)})

async def get_sse_service(kafka_producer:KafkaProducerService = Depends(get_kafka_producer_service)):
    return SSEService(kafka_producer)
