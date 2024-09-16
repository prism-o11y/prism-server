import os
from typing import List

from pydantic import BaseModel, Field
from uvicorn.workers import UvicornWorker


class HeadlessUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "auto", "http": "auto", "server_header": False}


class ServerConfig(BaseModel):
    NAME: str = os.getenv("SERVER_NAME")
    VERSION: str = os.getenv("SERVER_VERSION")
    ADDR: str = os.getenv("SERVER_ADDR")
    ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: _load_list_from_env("SERVER_ALLOWED_ORIGINS"))
    ALLOWED_HEADERS: List[str] = Field(default_factory=lambda: _load_list_from_env("SERVER_ALLOWED_HEADERS"))


def _load_list_from_env(key: str) -> List[str]:
    return os.getenv(key, "").split(",")
