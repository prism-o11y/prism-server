from pydantic import BaseModel
import os

class KafkaConfig(BaseModel):

    BROKERS: str = os.getenv("DATABASE_KAFKA_ADDR")

    TOPIC: str = os.getenv("DATABASE_KAFKA_TOPICS")

    GROUP_ID: str = os.getenv("DATABASE_KAFKA_CONSUMER_GROUPS")