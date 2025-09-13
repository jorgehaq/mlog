from fastapi import APIRouter, Depends, Query
from app.schemas.events import EventCreate, EventResponse
from app.services.event_service import log_event, get_events_by_service
from app.api.deps import get_db
from app.core.auth import require_auth


router = APIRouter()


@router.post("/", response_model=EventResponse, dependencies=[Depends(require_auth)])
async def create_event(event: EventCreate, db = Depends(get_db)):
    event_id = await log_event(db, event)
    return EventResponse(id=event_id, **event.model_dump())


@router.get("/{service}", dependencies=[Depends(require_auth)])
async def list_events(
    service: str,
    limit: int = Query(default=50, ge=1, le=200),
    cursor: str | None = Query(default=None),
    db = Depends(get_db),
):
    items, next_cursor = await get_events_by_service(db, service, limit=limit, cursor=cursor)
    return {"items": [i.model_dump() for i in items], "next_cursor": next_cursor}
