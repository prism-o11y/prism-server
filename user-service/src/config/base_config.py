from functools import lru_cache

from pydantic_settings import BaseSettings

from src.config.database_config import DatabaseConfig
from src.config.server_config import ServerConfig


class BaseConfig(BaseSettings):
    SERVER: ServerConfig = ServerConfig()
    DATABASE: DatabaseConfig = DatabaseConfig()


@lru_cache()
def get_base_config() -> BaseConfig:
    return BaseConfig()
