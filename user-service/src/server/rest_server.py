from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from src.config.base_config import BaseConfig


class RestServer:
    def __init__(self, config: BaseConfig) -> None:
        self._app = FastAPI(root_path="/api", title=config.SERVER.NAME, version=config.SERVER.VERSION)
        self._setup_middlewares(config)
        self._setup_routes(config)

    def _setup_middlewares(self, config: BaseConfig) -> None:
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=config.SERVER.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=config.SERVER.ALLOWED_HEADERS,
        )

        @self._app.middleware("http")
        async def _(request: Request, call_next):
            response = await call_next(request)
            del response.headers["server"]
            return response

    def _setup_routes(self, config: BaseConfig) -> None:
        pass

    def get_app(self) -> FastAPI:
        return self._app