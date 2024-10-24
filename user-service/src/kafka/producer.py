from confluent_kafka import Producer
from fastapi import Depends
from src.config.base_config import get_base_config, BaseConfig
from .message_model import KafkaMessage
from src.config.producer_config import ProducerConfig

class KafkaProducer:

    def __init__(self, baseConfig:BaseConfig):


        
        config: ProducerConfig = baseConfig.USER_PRODUCER

        

        producer_config = {
            "bootstrap.servers": config.bootstrap_servers,
            "security.protocol": config.security_protocol,
            "client.id": config.client_id
        }

        self.producer = Producer(producer_config)

    def produce(self, topic:str, data: KafkaMessage):

        def delivery_report(err, msg):

            if err is not None:
                print(f"Message delivery failed: {err}")
                raise Exception(f"Message delivery failed: {err}")
            else:
                print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

        try:
            self.producer.produce(topic, data.model_dump_json().encode('utf-8'), callback=delivery_report)


        except Exception as e:
            print(f"Failed to produce message to Kafka: {str(e)}")
            raise e
        
async def get_producer(config:BaseConfig = Depends(get_base_config)) -> Producer:

    return KafkaProducer(config)

    

        
        