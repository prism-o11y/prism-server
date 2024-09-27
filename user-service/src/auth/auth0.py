import logging
from fastapi import Request
from authlib.integrations.starlette_client import OAuth
from src.config.base_config import BaseConfig


class Auth0Manager:
    def __init__(self, config: BaseConfig) -> None:
        self.config = config.AUTH0

        self.oauth: OAuth = OAuth()
        try:
            self.oauth.register(
                "auth0",
                client_id=self.config.AUTH0_CLIENT_ID,
                client_secret=self.config.AUTH0_CLIENT_SECRET,
                client_kwargs={
                    "scope":"openid profile email",
                },
                server_metadata_url=(
                    f"https://{self.config.AUTH0_DOMAIN}/.well-known/openid-configuration"
                ),
            )

            logging.info("Auth0 manage initialized.")
        
        except Exception as e:

            logging.error(f"Failed to initialize Auth0 manager: {e}", exc_info=True)


async def get_auth0_manager(request: Request) -> Auth0Manager:
    return request.app.state.auth0_manager
