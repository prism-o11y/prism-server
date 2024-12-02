from enum import StrEnum
from pydantic import BaseModel
import datetime as dt
from typing import Optional, Any, Dict

class AlertSeverity(StrEnum):
    Critical = "CRITICAL"
    Warning  = "WARNING"        
    Info = "INFO"


class SSENotification(BaseModel):
    ClientID: str
    Severity: AlertSeverity
    Message: str
    DateTime: dt.datetime
    TargetNodeID: Optional[str] = None
    OriginNodeID: Optional[str] = None
    IsForwarded: Optional[bool] = None


class Action(StrEnum):
    SSE = "SSE"
    SMTP = "SMTP"


class NotificationWrapper(BaseModel):
    Action: Action
    Data: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True
