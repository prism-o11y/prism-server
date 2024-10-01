import uuid
import datetime as dt
from typing import Optional

class User:

    def __init__(self, email: str, status_id:int, created_at:dt.datetime, updated_at:dt.datetime, org_id=None, last_login=None) -> None:

        self.id:uuid = uuid.uuid4()

        self.org_id:Optional[uuid.UUID] = org_id
    
        self.email = email

        self.status_id:int = status_id

        self.created_at = created_at

        self.updated_at = updated_at

        self.last_login = last_login



