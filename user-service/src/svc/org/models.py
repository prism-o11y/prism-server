from pydantic import BaseModel
import uuid, datetime as dt
from enum import Enum

class Org(BaseModel):
    org_id: uuid.UUID
    name: str
    status_id: int
    created_at: dt.datetime
    updated_at: dt.datetime

    @classmethod
    def create_org(cls, name:str) -> 'Org':
        now = dt.datetime.now(dt.timezone.utc)

        return cls(
            org_id = uuid.uuid4(),
            name = name,
            status_id = Status.ACTIVE.value,
            created_at = now,
            updated_at = now,
        )

class Status(Enum):
    ACTIVE = 1
    REMOVED = 2
    PENDING = 3


    
