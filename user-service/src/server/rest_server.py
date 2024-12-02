import logging, os, asyncio
from typing import AsyncGenerator, Awaitable, Callable
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Response
from ..jwt.service import get_jwt_manager, JWTManager
from fastapi.concurrency import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware
from src.api.v1.entry import new_v1_router
from src.config.base_config import BaseConfig
from src.database.postgres import PostgresManager
from src.svc.auth.service import Auth0Manager
from src.kafka.producer import KafkaProducerService
from src.kafka.consumer import KafkaConsumerService
from src.svc.org.service import OrgService
from src.svc.user.service import UserService
from src.svc.apps.service import AppService
from src.svc.sse.service import SSEService

class RestServer:
    def __init__(self, config: BaseConfig) -> None:
        self._app = FastAPI(
            root_path="/",
            title=config.SERVER.NAME,
            version=config.SERVER.VERSION,
            lifespan=self.lifespan_context,
        )
        self.config = config
        self._app.state.postgres_manager = PostgresManager(config)
        self._app.state.auth0_manager = Auth0Manager(config)
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
        self._app.add_middleware(
            SessionMiddleware,
            secret_key=os.getenv("SECRET_KEY"),
        )

        @self._app.middleware("http")
        async def remove_server_header(
            request: Request, call_next: Callable[[Request], Awaitable[Response]]
        ) -> Response:
            response = await call_next(request)
            if "server" in response.headers:
                del response.headers["server"]
                logging.debug("Removed server header.")
            return response

    def _setup_routes(self) -> None:
        v1_router = new_v1_router()
        self._app.include_router(v1_router)

    @asynccontextmanager
    async def lifespan_context(self, app: FastAPI) -> AsyncGenerator[None, None]:
        
        postgres_manager: PostgresManager = app.state.postgres_manager
        await postgres_manager.connect()
        kafka_producer: KafkaProducerService = KafkaProducerService(self.config.KAFKA)
        app.state.kafka_producer = kafka_producer
        jwt_manager:JWTManager = JWTManager()
        await kafka_producer.start()



        sse_svc: SSEService = SSEService(
            kafka_producer
        )

        org_svc: OrgService = OrgService(
            postgres_manager,
            kafka_producer,
            sse_svc
        )

        sse_svc: SSEService = SSEService(
            kafka_producer
        )

        app_svc: AppService = AppService(
            postgres_manager,
            kafka_producer,
            sse_svc
        )

        user_svc: UserService = UserService(
            postgres_manager,
            kafka_producer,
            jwt_manager,
            sse_svc
        )

        kafka_consumer: KafkaConsumerService = KafkaConsumerService(
            self.config.KAFKA,
            user_svc,
            org_svc,
            app_svc
        )
        
        app.state.kafka_consumer = kafka_consumer
        await kafka_consumer.start_user_consumer()

        try:        
            yield

        finally:

            logging.info("Starting graceful shutdown...")
            await kafka_consumer.stop_user_consumer()
            await kafka_producer.stop()
            await postgres_manager.disconnect()
            logging.info("All services stopped successfully.")

            logging.shutdown()


    def get_app(self) -> FastAPI:
        return self._app