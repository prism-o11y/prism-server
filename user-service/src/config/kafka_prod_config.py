from pydantic import BaseModel

class UserProducerConfig(BaseModel):
    bootstrap_servers: str = "kafka:9092"
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: str = None
    sasl_username: str = None
    sasl_password: str = None
    client_id: str = "user-producer"
    



    
