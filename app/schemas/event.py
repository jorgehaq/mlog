from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    service: str = Field(..., examples=["axi", "mint"]) 
    action: str = Field(..., examples=["login", "purchase"]) 
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[datetime] = None


class EventResponse(EventCreate):
    id: str = Field(..., description="ID del evento")

