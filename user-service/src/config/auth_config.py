import os

from pydantic import BaseModel


class Auth0Config(BaseModel):
    AUTH0_DOMAIN:str = os.getenv("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID:str = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET:str = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_AUTHORIZE_URL:str = f"https://{AUTH0_DOMAIN}/authorize"
    AUTH0_ACCESS_TOKEN_URL:str = f"https://{AUTH0_DOMAIN}/oauth/token"
    AUTH0_AUDIENCE:str = f"https://{AUTH0_DOMAIN}/api/v2/"
    AUTH0_MANAGEMENT_API_URL:str = f"https://{AUTH0_DOMAIN}/api/v2/users"
    AUTH0_JWKS_URL:str = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"