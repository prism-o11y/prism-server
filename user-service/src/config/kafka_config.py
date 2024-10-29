from pydantic import BaseModel
import os

class KafkaConfig(BaseModel):

    BROKER: str = os.getenv("DATABASE_KAFKA_ADDR")

    TOPIC: str = next(
        (topic for topic in os.getenv("DATABASE_KAFKA_TOPICS", "").split(",") if "user" in topic), None
    )

    GROUP_ID: str = next(
        (group for group in os.getenv("DATABASE_KAFKA_CONSUMER_GROUPS", "").split(",") if "user" in group), None
    )

