import uuid
import datetime as dt

class User:

    def __init__(self, email: str) -> None:

        self.id:uuid = uuid.uuid4()

        self.org_id:uuid = None
    
        self.email = email

        self.status:int = None

        self.created_at = None

        self.updated_at = None

        self.last_login = None