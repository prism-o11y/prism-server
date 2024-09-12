from pydantic_settings import BaseSettings

from prism.src.config.server import ServerConfig


class BaseConfig(BaseSettings):
    SERVER: ServerConfig = ServerConfig()
