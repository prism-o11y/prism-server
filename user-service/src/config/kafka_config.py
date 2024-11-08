from pydantic import BaseModel, Field
import os
from typing import Dict


class KafkaConfig(BaseModel):
    BROKER: str = os.getenv("DATABASE_KAFKA_ADDR")
    TOPICS: Dict[str,str] = Field(default_factory=lambda:_load_dict_from_env("DATABASE_KAFKA_TOPICS"))
    CONSUMER_GROUPS: Dict[str,str] = Field(default_factory=lambda:_load_dict_from_env("DATABASE_KAFKA_CONSUMER_GROUPS"))


def _load_dict_from_env(key: str) -> Dict[str, str]:
    items = os.getenv(key, "").split(",")
    return {item.split("-")[0]: item for item in items if "-" in item}

