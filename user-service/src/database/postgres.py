from typing import AsyncGenerator

import asyncpg
from fastapi import Depends
from fastapi.concurrency import asynccontextmanager
from src.config.base_config import BaseConfig


class PostgresManager:
    def __init__(self, config: BaseConfig) -> None:
        self.config = config.DATABASE
        self.pool: asyncpg.Pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.config.POSTGRES_URL)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def get_connection(self):
        connection = await self.pool.acquire()
        try:
            yield connection
        finally:
            await self.pool.release(connection)


async def get_db_connection(manager: PostgresManager = Depends()) -> AsyncGenerator[asyncpg.Connection, None]:
    async with manager.get_connection() as connection:
        yield connection
