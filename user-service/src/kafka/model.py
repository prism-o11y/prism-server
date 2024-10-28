from pydantic import BaseModel

class KafkaMessage(BaseModel):

    action: str

    data: dict