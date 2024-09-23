import logging

from authlib.integrations.starlette_client import OAuth
from fastapi import Request

from src.config.base_config import BaseConfig


class Auth0Manager:
    def __init__(self, config: BaseConfig) -> None:
        self.config = config.AUTH0
        self.auth0: OAuth = OAuth()

        try:
            self.auth0.register(
                name="auth0",
                client_id=self.config.AUTH0_CLIENT_ID,
                client_secret=self.config.AUTH0_CLIENT_SECRET,
                client_kwargs={"scope": "openid profile email"},
                authorize_url=f"https://{self.config.AUTH0_DOMAIN}/authorize",
                access_token_url=f"https://{self.config.AUTH0_DOMAIN}/oauth/token",
            )

            logging.info("Auth0 manager initialized.")

        except Exception as e:
            logging.error(f"Failed to initialize Auth0 manager: {e}", exc_info=True)


async def get_auth0_manager(request: Request) -> Auth0Manager:
    return request.app.state.auth0_manager
