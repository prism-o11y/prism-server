import uuid
from typing import Optional
import datetime as dt
from pydantic import BaseModel


class User(BaseModel):

    id: uuid.UUID

    org_id: Optional[uuid.UUID]

    email: str

    status_id: int

    created_at: dt.datetime

    updated_at: dt.datetime

    last_login: dt.datetime | None



