from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.events import EventCreate, EventResponse
from typing import List, Optional, Tuple
from pymongo.errors import DuplicateKeyError
from app.core.config import settings
from bson import ObjectId


async def log_event(db: "AsyncIOMotorDatabase", event: EventCreate) -> str:
    event_doc = event.model_dump()
    if not event_doc.get("schema_version"):
        event_doc["schema_version"] = settings.EVENT_SCHEMA_VERSION
    try:
        result = await db.audit_logs.insert_one(event_doc)
    except DuplicateKeyError:
        # Propagar para que el endpoint responda 409
        raise
    return str(result.inserted_id)


async def get_events_by_service(
    db: "AsyncIOMotorDatabase", service: str, *, limit: int = 50, cursor: Optional[str] = None
) -> Tuple[List[EventResponse], Optional[str]]:
    q = {"service": service}
    if cursor:
        try:
            q["_id"] = {"$gt": ObjectId(cursor)}
        except Exception:
            pass
    limit = max(1, min(limit, 200))
    cursor_db = (
        db.audit_logs.find(q)
        .sort("_id", 1)
        .limit(limit + 1)
    )
    out: List[EventResponse] = []
    last_id: Optional[str] = None
    async for doc in cursor_db:
        last_id = str(doc.get("_id"))
        out.append(
            EventResponse(
                id=last_id,
                timestamp=doc.get("timestamp"),
                service=doc.get("service"),
                user_id=doc.get("user_id"),
                action=doc.get("action"),
                metadata=doc.get("metadata", {}),
            )
        )
    next_cursor = None
    if len(out) > limit:
        out = out[:limit]
        next_cursor = last_id
    return out, next_cursor
