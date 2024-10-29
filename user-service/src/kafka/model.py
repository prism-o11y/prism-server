from pydantic import BaseModel
from enum import StrEnum

# class KafkaMessage(BaseModel):

#     action: str

#     data: dict

class KafkaMessage(BaseModel):

    data: bytes

    service: str

    email: str

    user_id: str

class KafkaData(BaseModel):

    action: str

    user_data: dict



class Action(StrEnum):

    INSERT_USER = "insert_user"

    UPDATE_USER = "update_user"

    DELETE_USER = "delete_user"

class Service(StrEnum):

    USER = "user"

    ALERT = "alert"

    LOG = "log"


