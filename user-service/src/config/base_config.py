from functools import lru_cache

from pydantic_settings import BaseSettings

from src.config.server_config import ServerConfig


class BaseConfig(BaseSettings):
    SERVER: ServerConfig = ServerConfig()


@lru_cache()
def get_base_config() -> BaseConfig:
    return BaseConfig()
