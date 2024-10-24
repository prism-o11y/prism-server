from pydantic import BaseModel
import datetime as dt
from src.kafka.events import USER_EVENTS

class KafkaMessage(BaseModel):
    event: USER_EVENTS
    payload: dict
    timestamp: dt.datetime

    class Config: 
        json_encoders = {
            dt.datetime: lambda v: v.isoformat(),      
        }