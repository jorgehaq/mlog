from fastapi import APIRouter, Depends
from app.schemas.events import EventCreate, EventResponse
from app.services.event_service import log_event
from app.api.deps import get_db


router = APIRouter()


@router.post("/", response_model=EventResponse)
async def create_event(event: EventCreate, db = Depends(get_db)):
    event_id = await log_event(db, event)
    return EventResponse(id=event_id, **event.model_dump())

