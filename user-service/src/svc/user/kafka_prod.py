from confluent_kafka import Producer
from src.config.base_config import get_base_config
from src.svc.user.user_model import User
import logging

class UserProducer:

    def __init__(self):

        config = get_base_config().USER_PRODUCER

        producer_config = {
            "bootstrap.servers": config.bootstrap_servers,
            "client.id": config.client_id,
        }

        if config.security_protocol != "PLAINTEXT":

            producer_config.update({
                "security.protocol": config.security_protocol,
                "sasl.mechanisms": config.sasl_mechanism,
                "sasl.username": config.sasl_username,
                "sasl.password": config.sasl_password
            })

        self.producer = Producer(producer_config)

    def produce(self, topic: str, user: User):

        message = user.model_dump_json() 

        def delivery_report(err, msg):

            if err is not None:
                logging.error(f"Message delivery failed: {err}")
            else:
                logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

        
        self.producer.produce(topic, message.encode('utf-8'), callback=delivery_report)

        self.producer.flush()

async def get_user_producer() -> UserProducer:

    return UserProducer()



            
