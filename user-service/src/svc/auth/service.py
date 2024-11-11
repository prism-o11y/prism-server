import logging
from fastapi import Request
from authlib.integrations.starlette_client import OAuth
from src.config.base_config import BaseConfig
import jwt, httpx
from jwt import PyJWKClient


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

    
    async def get_decoded_token(self, id_token:str):

        decode_token = None

        try:

            jwks_url = self.config.AUTH0_JWKS_URL
            jwks_client = PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)
            decode_token = jwt.decode(
                id_token,
                signing_key.key,
                algorithms = ["RS256"],
                audience = self.config.AUTH0_CLIENT_ID,
                issuer = f"https://{self.config.AUTH0_DOMAIN}/"
            )
        
        except jwt.ExpiredSignatureError as e:
            logging.error(f"Token has expired: {e}")
            return None
        
        except jwt.InvalidTokenError as e:
            logging.error(f"Invalid token: {e}")
            return None
        
        logging.info("Successfully decoded token.")

        return decode_token
    
    async def get_management_token(self):

        access_token_url:str = self.config.AUTH0_ACCESS_TOKEN_URL

        payload = {
            "client_id": self.config.AUTH0_CLIENT_ID,
            "client_secret": self.config.AUTH0_CLIENT_SECRET,
            "audience": self.config.AUTH0_AUDIENCE,
            "grant_type": "client_credentials"
        }

        headers = {
            "content-type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                access_token_url,
                json=payload,
                headers=headers
            )

            response.raise_for_status()
            data = response.json()
            return data.get("access_token")
        
    def get_logout_url(self, return_url:str) -> str:
        return self.config.AUTH0_LOGOUT_URL + f"&returnTo={return_url}"


async def get_auth0_manager(request: Request) -> Auth0Manager:
    return request.app.state.auth0_manager
