from fastapi import FastAPI, Request
from src.api.v1.entry import new_v1_router
from src.config.base_config import BaseConfig
from starlette.middleware.cors import CORSMiddleware
import logging
from typing import AsyncGenerator, Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.concurrency import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware

from src.api.v1.entry import new_v1_router
from src.config.base_config import BaseConfig
from src.database.postgres import PostgresManager


class RestServer:
    def __init__(self, config: BaseConfig) -> None:
        self._app = FastAPI(
            root_path="/api",
            title=config.SERVER.NAME,
            version=config.SERVER.VERSION,
            lifespan=self.lifespan_context,
        )
        self._app.state.postgres_manager = PostgresManager(config)
        self._setup_middlewares(config)
        self._setup_routes()
        logging.info("REST server initialized.")

    def _setup_middlewares(self, config: BaseConfig) -> None:
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=config.SERVER.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=config.SERVER.ALLOWED_HEADERS,
        )

        @self._app.middleware("http")
        async def remove_server_header(
            request: Request, call_next: Callable[[Request], Awaitable[Response]]
        ) -> Response:
            response = await call_next(request)
            response.headers.pop("server", None)
            logging.debug("Removed server header.")
            return response

    def _setup_routes(self) -> None:
        v1_router = new_v1_router()
        self._app.include_router(v1_router)

    @asynccontextmanager
    async def lifespan_context(self, app: FastAPI) -> AsyncGenerator[None, None]:
        postgres_manager: PostgresManager = app.state.postgres_manager
        await postgres_manager.connect()
        yield
        await postgres_manager.disconnect()

    def get_app(self) -> FastAPI:
        return self._app
