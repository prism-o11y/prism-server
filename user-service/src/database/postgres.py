import logging
from typing import AsyncGenerator

from asyncpg import Connection, Pool, create_pool
from fastapi import Depends, Request
from fastapi.concurrency import asynccontextmanager
from src.config.base_config import BaseConfig


class PostgresManager:
    def __init__(self, config: BaseConfig) -> None:
        self.config = config.DATABASE
        self.pool: Pool = None

    async def connect(self) -> None:
        try:
            self.pool = await create_pool(dsn=self.config.POSTGRES_URL)
        except Exception as e:
            logging.critical(f"Failed to connect to Postgres: {e}", exc_info=True)
            exit(1)

    async def disconnect(self) -> None:
        if self.pool:
            try:
                await self.pool.close()
            except Exception as e:
                logging.error(f"Failed to close Postgres connection: {e}", exc_info=True)

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Connection, None]:
        connection = await self.pool.acquire()
        try:
            logging.debug("PostgreSQL connection acquired.")
            yield connection
        finally:
            await self.pool.release(connection)
            logging.debug("PostgreSQL connection released.")


async def get_postgres_manager(request: Request) -> PostgresManager:
    return request.app.state.postgres_manager


async def get_db_connection(
    postgres_manager: PostgresManager = Depends(get_postgres_manager),
) -> AsyncGenerator[Connection, None]:
    async with postgres_manager.get_connection() as connection:
        yield connection