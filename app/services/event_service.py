from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schemas.events import EventCreate


async def log_event(db: "AsyncIOMotorDatabase", event: EventCreate) -> str:
    event_doc = event.model_dump()
    result = await db.audit_logs.insert_one(event_doc)
    return str(result.inserted_id)

