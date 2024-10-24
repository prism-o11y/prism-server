from functools import lru_cache
import os
from pydantic_settings import BaseSettings
from src.config.auth_config import Auth0Config
from src.config.database_config import DatabaseConfig
from src.config.server_config import ServerConfig
from src.config.producer_config import ProducerConfig
from src.config.auth_config import Auth0Config


class BaseConfig(BaseSettings):
    SERVER: ServerConfig = ServerConfig()
    AUTH0: Auth0Config = Auth0Config()
    DATABASE: DatabaseConfig = DatabaseConfig()

    USER_PRODUCER: ProducerConfig = ProducerConfig(
        bootstrap_servers="kafka:9092",
        security_protocol="SASL_PLAINTEXT",
        client_id="user-producer"
    )

@lru_cache()
def get_base_config() -> BaseConfig:
    return BaseConfig()

