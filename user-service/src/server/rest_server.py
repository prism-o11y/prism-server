from fastapi import FastAPI, Request
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
        self._config = config
        self._database_manager = PostgresManager(config)
        self._setup_middlewares()
        self._setup_routes()

    def _setup_middlewares(self) -> None:
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=self._config.SERVER.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=self._config.SERVER.ALLOWED_HEADERS,
        )

        @self._app.middleware("http")
        async def _(request: Request, call_next):
            response = await call_next(request)
            del response.headers["server"]
            return response

    def _setup_routes(self) -> None:
        v1_router = new_v1_router()
        self._app.include_router(v1_router)

    @asynccontextmanager
    async def lifespan_context(self, app: FastAPI):
        await self._database_manager.connect()
        yield
        await self._database_manager.disconnect()

    def get_app(self) -> FastAPI:
        return self._app
