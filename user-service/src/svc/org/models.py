from pydantic import BaseModel
import uuid, datetime as dt
from enum import Enum

class Org(BaseModel):
    org_id: uuid.UUID
    name: str
    status_id: int
    created_at: dt.datetime
    updated_at: dt.datetime
    org_password: str

class Status(Enum):
    ACTIVE = 1
    REMOVED = 2
    PENDING = 3


    
