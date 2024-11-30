from pydantic import BaseModel
import uuid, datetime as dt

class Application(BaseModel):
    
    app_id: uuid.UUID
    org_id: uuid.UUID
    app_name: str
    app_url: str
    created_at: dt.datetime
    updated_at: dt.datetime

    @classmethod
    def create_application(cls, org_id:uuid.UUID, app_name:str, app_url:str) -> 'Application':
        now = dt.datetime.now(dt.timezone.utc)

        return cls(
            app_id = uuid.uuid4(),
            org_id = org_id,
            app_name = app_name,
            app_url = app_url,
            created_at = now,
            updated_at = now,
        )