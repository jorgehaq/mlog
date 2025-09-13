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

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        def _check(d: Dict[str, Any], path: str = ""):
            if len(d) > 1000:
                raise ValueError("metadata too large")
            for k, val in d.items():
                if k.startswith("$") or "." in k:
                    raise ValueError("invalid metadata key")
                if isinstance(val, dict):
                    _check(val, path + "." + k if path else k)
        _check(v)
        return v


class EventResponse(EventCreate):
    id: str


class EventListResponse(BaseModel):
    items: list[EventResponse]
    next_cursor: str | None = None
