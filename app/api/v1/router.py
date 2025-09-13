from fastapi import APIRouter, Depends

from app.schemas.event import EventCreate, EventResponse
from app.schemas.analytics import AnalyticsSummary, TimelineResponse
from app.services.events_service import EventsService
from app.core import db


router = APIRouter()


def get_service() -> EventsService:
    # En el futuro podemos inyectar un repo de Mongo si MONGO_URI está presente
    return EventsService()


@router.post("/events", response_model=EventResponse)
async def create_event(payload: EventCreate, svc: EventsService = Depends(get_service)):
    return await svc.create_event(payload)


@router.get("/events/{service}", response_model=list[EventResponse])
async def list_events(service: str, svc: EventsService = Depends(get_service)):
    return await svc.list_by_service(service)


@router.get("/analytics/summary", response_model=AnalyticsSummary)
async def analytics_summary(svc: EventsService = Depends(get_service)):
    return await svc.analytics_summary()


@router.get("/analytics/timeline", response_model=TimelineResponse)
async def analytics_timeline(svc: EventsService = Depends(get_service)):
    return await svc.analytics_timeline()


@router.get("/health")
async def health():
    # Si hay Mongo, reportamos su estado; si no, ok=false para DB, pero API sigue viva.
    mongo_ok = await db.ping()
    return {"status": "ok", "mongo": mongo_ok}

