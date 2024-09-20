from functools import lru_cache

from pydantic_settings import BaseSettings
from src.config.auth_config import Auth0Config
from src.config.server_config import ServerConfig


class BaseConfig(BaseSettings):
    SERVER: ServerConfig = ServerConfig()
    AUTH0: Auth0Config = Auth0Config()


@lru_cache()
def get_base_config() -> BaseConfig:
    return BaseConfig()
