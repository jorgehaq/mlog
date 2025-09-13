from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    by_action: Dict[str, int]
    total: int


class TimelinePoint(BaseModel):
    ts: datetime
    count: int


class TimelineResponse(BaseModel):
    points: List[TimelinePoint]

