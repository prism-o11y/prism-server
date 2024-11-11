from pydantic import BaseModel
import os

class JWTConfig(BaseModel):

    SECRET_KEY: str = os.getenv("JWT_SECRET")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM")

    