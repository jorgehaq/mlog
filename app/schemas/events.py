from pydantic import BaseModel
from typing import Any, Dict
from datetime import datetime


class EventCreate(BaseModel):
    timestamp: datetime
    service: str
    user_id: str
    action: str
    metadata: Dict[str, Any]


class EventResponse(EventCreate):
    id: str

