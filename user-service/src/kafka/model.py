from enum import StrEnum
from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
import json

class SourceType(StrEnum):
    ALERT_NOTI_SERVICE = "alert-noti-service"
    LOG_SERVICE = "log-service"
    USER_SERVICE = "user-service"

class EventData(BaseModel):
    source: SourceType
    data: bytes
    email: Optional[EmailStr] = None
    user_id: UUID

    @classmethod
    def decode_message(cls, message: bytes) -> "EventData":
        try:
            data_dict = json.loads(message.decode("utf-8"))
            return cls(**data_dict)
        
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            return None
        
        except ValueError as e:
            print(f"Error in data validation: {e}")
            return None

class KafkaData(BaseModel):
    action: str
    user_data: dict

    @classmethod
    def decode_data(cls, data: bytes) -> "KafkaData":
        try:
            kafka_data_dict = json.loads(data.decode("utf-8"))
            return KafkaData(**kafka_data_dict)
        
        except json.JSONDecodeError as e:
            print(f"Failed to decode KafkaData JSON: {e}")
            return None
        
        except ValueError as e:
            print(f"Error in KafkaData validation: {e}")
            return None

class Action(StrEnum):
    INSERT_USER = "insert_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"

class Topic(StrEnum):
    USER = "user-topic"
    ALERT = "alert-topic"
    LOG = "log-topic"
