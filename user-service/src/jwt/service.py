import jwt, datetime, uuid, logging
from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR
from ..config.base_config import get_base_config

class JWTManager:

    def __init__(self):
        config = get_base_config().JWT
        self.secret = config.SECRET_KEY
        self.algorithm = config.ALGORITHM

    async def encode(self, user_id: uuid.UUID, auth_sub: str) -> str:

        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "user_id": str(user_id),
            "auth_sub": auth_sub,
            "exp": now + datetime.timedelta(days=1),
            "iat": now
        }

        try:
            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            return token
        
        except Exception as e:
            logging.exception({"event": "JWT encode error", "error": str(e), "status": "Failed"})
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Token creation failed")

    async def decode(self, token: str) -> dict:
        try:
            decoded_token = jwt.decode(token, key=self.secret, algorithms=[self.algorithm])
            return decoded_token
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token has expired")
        
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
    async def validate_jwt(self, token:str) -> tuple[bool, dict | None]:
        try:
            decoded_token = await self.decode(token)
            return (True, decoded_token)
        
        except HTTPException as e:
            logging.info({"event": "JWT validation", "status": "Invalid or expired", "detail": e.detail})
            return (False,None)

        
async def get_jwt_manager() -> JWTManager:
    return JWTManager()




