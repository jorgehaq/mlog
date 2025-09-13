from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from app.schemas.event import EventCreate, EventResponse
from app.schemas.analytics import AnalyticsSummary, TimelinePoint, TimelineResponse


class InMemoryRepo:
    def __init__(self) -> None:
        self._items: List[Dict[str, Any]] = []

    async def insert(self, doc: Dict[str, Any]) -> str:
        doc_id = str(len(self._items) + 1)
        doc["_id"] = doc_id
        self._items.append(doc)
        return doc_id

    async def find_by_service(self, service: str) -> List[Dict[str, Any]]:
        return [d for d in self._items if d.get("service") == service]

    async def all(self) -> List[Dict[str, Any]]:
        return list(self._items)


class EventsService:
    def __init__(self, repo: Optional[InMemoryRepo] = None) -> None:
        # Para desarrollo, usar repo en memoria.
        self.repo = repo or InMemoryRepo()

    async def create_event(self, data: EventCreate) -> EventResponse:
        payload = data.model_dump()
        if not payload.get("timestamp"):
            payload["timestamp"] = datetime.utcnow()
        _id = await self.repo.insert(payload)
        logger.debug("Evento creado: {}", _id)
        return EventResponse(id=_id, **data.model_dump())

    async def list_by_service(self, service: str) -> List[EventResponse]:
        docs = await self.repo.find_by_service(service)
        return [
            EventResponse(
                id=str(d.get("_id")),
                service=d.get("service"),
                action=d.get("action"),
                payload=d.get("payload", {}),
                timestamp=d.get("timestamp"),
            )
            for d in docs
        ]

    async def analytics_summary(self) -> AnalyticsSummary:
        items = await self.repo.all()
        by_action = Counter([d.get("action") for d in items if d.get("action")])
        return AnalyticsSummary(by_action=dict(by_action), total=len(items))

    async def analytics_timeline(self) -> TimelineResponse:
        items = await self.repo.all()
        buckets: Dict[str, int] = defaultdict(int)
        for d in items:
            ts: Optional[datetime] = d.get("timestamp")
            if not ts:
                continue
            key = ts.replace(second=0, microsecond=0).isoformat()
            buckets[key] += 1
        points = [
            TimelinePoint(ts=datetime.fromisoformat(k), count=v)
            for k, v in sorted(buckets.items())
        ]
        return TimelineResponse(points=points)

