import logging
from typing import AsyncGenerator

import asyncpg
from fastapi import Depends
from fastapi.concurrency import asynccontextmanager
from src.config.base_config import BaseConfig


class PostgresManager:
    def __init__(self, config: BaseConfig) -> None:
        self.config = config.DATABASE
        self.pool: asyncpg.Pool = None

    async def connect(self) -> None:
        try:
            self.pool = await create_pool(dsn=self.config.POSTGRES_URL)
        except Exception as e:
            logging.critical(f"Failed to connect to Postgres: {e}", exc_info=True)
            exit(1)

    async def disconnect(self):
        if self.pool:
            try:
                await self.pool.close()
            except Exception as e:
                logging.error(f"Failed to close Postgres connection: {e}", exc_info=True)

    @asynccontextmanager
    async def get_connection(self):
        connection = await self.pool.acquire()
        try:
            logging.debug("PostgreSQL connection acquired.")
            yield connection
        finally:
            await self.pool.release(connection)
            logging.debug("PostgreSQL connection released.")


async def get_db_connection(manager: PostgresManager = Depends()) -> AsyncGenerator[asyncpg.Connection, None]:
    async with manager.get_connection() as connection:
        yield connection
