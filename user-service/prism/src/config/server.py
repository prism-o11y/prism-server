from dataclasses import dataclass

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings


@dataclass
class ServerConfig:
    ADDR: str = Config("ADDR", default=False)
    ALLOWED_ORIGINS: list[str] = Config("ALLOWED_ORIGINS", cast=CommaSeparatedStrings)
    ALLOWED_HEADERS: list[str] = Config("ALLOWED_HEADERS", cast=CommaSeparatedStrings)
