from pydantic import BaseModel

class ProducerConfig(BaseModel):
    bootstrap_servers: str
    security_protocol: str
    client_id: str
    