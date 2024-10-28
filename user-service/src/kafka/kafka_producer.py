from aiokafka import AIOKafkaProducer
import json, logging

class ProducerManager:

    def __init__(self, broker):
        self.broker = broker
        self.producer = None

    async def init_producer(self):

        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        await self.producer.start()

        logging.info("Kafka producer initialized.")

    async def stop_producer(self):

        if self.producer:

            await self.producer.stop()

            logging.info("Kafka producer stopped.")

    async def send_message(self, topic, message):
        try:
            await self.producer.send_and_wait(topic, message)
            logging.info(f"Message sent to topic {topic}")
        
        except Exception as e:
            logging.exception(f"Failed to send message to topic {topic}: {e}")