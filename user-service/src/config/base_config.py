from functools import lru_cache
from pydantic_settings import BaseSettings
from .auth_config import Auth0Config
from .database_config import DatabaseConfig
from .server_config import ServerConfig
from .auth_config import Auth0Config
from .kafka_config import KafkaConfig
from .jwt_config import JWTConfig

class BaseConfig(BaseSettings):
    SERVER: ServerConfig = ServerConfig()
    AUTH0: Auth0Config = Auth0Config()
    DATABASE: DatabaseConfig = DatabaseConfig()
    KAFKA: KafkaConfig = KafkaConfig()
    JWT: JWTConfig = JWTConfig()

@lru_cache()
def get_base_config() -> BaseConfig:
    return BaseConfig()