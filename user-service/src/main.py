import logging

from fastapi import FastAPI
from pydantic import ValidationError

from src.config.base_config import get_base_config
from src.server.rest_server import RestServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def entry() -> FastAPI:
    try:
        config = get_base_config()
    except ValidationError as e:
        print("Configuration Error:", e)

    rest_server = RestServer(config)
    return rest_server.get_app()
