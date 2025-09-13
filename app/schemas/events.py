from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict
from datetime import datetime, timezone


class EventCreate(BaseModel):
    timestamp: datetime
    service: str = Field(..., pattern=r"^[a-z0-9_-]{2,32}$")
    user_id: str = Field(..., min_length=1, max_length=64)
    action: str = Field(..., min_length=1, max_length=64)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def ensure_timezone(cls, v: datetime) -> datetime:
        # Normalizar a aware en UTC si viene naive
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class EventResponse(EventCreate):
    id: str
