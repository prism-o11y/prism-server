import os

from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    POSTGRES_URL: str = os.getenv("DATABASE_POSTGRES_URL")
