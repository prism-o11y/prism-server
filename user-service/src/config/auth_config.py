import os

from pydantic import BaseModel


class Auth0Config(BaseModel):
    AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID: str = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET: str = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_API_AUDIENCE: str = os.getenv("AUTH0_API_AUDIENCE")
    AUTH0_URL: str = os.getenv("AUTH0_URL")
    AUTH0_ALGORITHMS: str = os.getenv("AUTH0_ALGORITHMS")
