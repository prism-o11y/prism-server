from fastapi import APIRouter, Request
from src.config.base_config import BaseConfig
from authlib.integrations.starlette_client import OAuth
import logging

def new_v1_router() -> APIRouter:
    from src.api.v1.auth import _router
    router = APIRouter(prefix="/v1")
    router.include_router(_router)
    return router


class Auth0Manager:

    def __init__(self, config: BaseConfig) -> None:

        self.config = config.AUTH0

        self.auth0: OAuth = OAuth()

        try :

            self.auth0.register(
                name="auth0",
                client_id=self.config.AUTH0_CLIENT_ID,
                client_secret=self.config.AUTH0_CLIENT_SECRET,
                client_kwargs={"scope": "openid profile email"},
                authorize_url=f'https://{self.config.AUTH0_DOMAIN}/authorize',
                access_token_url=f'https://{self.config.AUTH0_DOMAIN}/oauth/token',
            )

            logging.info("Auth0 manager initialized.")
        
        except Exception as e:

            logging.error(f'Failed to initialize Auth0 manager: {e}', exc_info=True)


async def get_auth0_manager(request: Request) -> Auth0Manager:
    return request.app.state.auth0_manager




    

