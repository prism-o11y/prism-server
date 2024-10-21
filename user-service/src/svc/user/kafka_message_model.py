from pydantic import BaseModel
import datetime as dt

class KafkaMessage(BaseModel):
    
    event: str

    payload: dict

    timestamp: dt.datetime

    class Config: 

        json_encoders = {

            dt.datetime: lambda v: v.isoformat(),
            
        }

