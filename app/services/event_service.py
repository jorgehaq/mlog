from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.events import EventCreate, EventResponse
from typing import List


async def log_event(db: "AsyncIOMotorDatabase", event: EventCreate) -> str:
    event_doc = event.model_dump()
    result = await db.audit_logs.insert_one(event_doc)
    return str(result.inserted_id)


async def get_events_by_service(db: "AsyncIOMotorDatabase", service: str) -> List[EventResponse]:
    cursor = db.audit_logs.find({"service": service}).sort("timestamp", 1)
    out: List[EventResponse] = []
    async for doc in cursor:
        out.append(
            EventResponse(
                id=str(doc.get("_id")),
                timestamp=doc.get("timestamp"),
                service=doc.get("service"),
                user_id=doc.get("user_id"),
                action=doc.get("action"),
                metadata=doc.get("metadata", {}),
            )
        )
    return out
