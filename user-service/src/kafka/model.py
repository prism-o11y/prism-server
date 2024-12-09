from enum import StrEnum
from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
import json, logging
from ..config.base_config import BaseConfig
import datetime as dt


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
            logging.exception(f"Failed to decode JSON: {e}")
            return None
        
        except ValueError as e:
            logging.exception(f"Error in data validation: {e}")
            return None

class Data(BaseModel):
    action: str
    data: dict

    @classmethod
    def decode_data(cls, data: bytes) -> "Data":
        try:
            kafka_data_dict = json.loads(data.decode("utf-8"))
            return Data(**kafka_data_dict)
        
        except json.JSONDecodeError as e:
            logging.exception(f"Failed to decode KafkaData JSON: {e}")
            return None
        
        except ValueError as e:
            logging.exception(f"Error in KafkaData validation: {e}")
            return None

class Action(StrEnum):
    INSERT_USER = "insert_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    INSERT_ORG = "insert_org"
    UPDATE_ORG = "update_org"
    DELETE_ORG = "delete_org"
    ADD_USER_TO_ORG = "add_user_to_org"
    REMOVE_USER_FROM_ORG = "remove_user_from_org"
    INSERT_APP = "insert_app"
    UPDATE_APP = "update_app"
    DELETE_APP = "delete_app"




