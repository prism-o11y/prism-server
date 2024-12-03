from enum import StrEnum
from pydantic import BaseModel
import datetime as dt
from typing import Optional, Any, Dict

class AlertSeverity(StrEnum):
    Critical = "CRITICAL"
    Warning  = "WARNING"        
    Info = "INFO"


class SSENotification(BaseModel):
    client_id: str
    connection_id:str
    severity: AlertSeverity
    message: str
    dateTime: dt.datetime
    target_node_id: Optional[str] = None
    origin_node_id: Optional[str] = None
    is_forwarded: Optional[bool] = None


class Action(StrEnum):
    SSE = "SSE"
    SMTP = "SMTP"


class NotificationWrapper(BaseModel):
    action: Action
    data: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

class SSEClients(StrEnum):
    TEST_CLIENT = "test-client"
