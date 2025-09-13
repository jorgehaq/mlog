from typing import Optional

import motor.motor_asyncio
from app.core.config import settings

DB_CLIENT: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None


def _build_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    return motor.motor_asyncio.AsyncIOMotorClient(
        settings.MONGO_URI,
        minPoolSize=settings.DB_MIN_POOL_SIZE,
        maxPoolSize=settings.DB_MAX_POOL_SIZE,
    )


def get_database():
    global DB_CLIENT
    if DB_CLIENT is None:
        DB_CLIENT = _build_client()
    return DB_CLIENT["mlog"]


async def connect_db():
    global DB_CLIENT
    if DB_CLIENT is None:
        DB_CLIENT = _build_client()
        # Ensure indexes
        db = DB_CLIENT["mlog"]
        try:
            await db.audit_logs.create_index([("service", 1), ("timestamp", -1)], name="svc_ts")
            await db.audit_logs.create_index([("action", 1)], name="action")
            await db.audit_logs.create_index([("service", 1), ("user_id", 1), ("timestamp", 1)], name="uniq_svc_user_ts", unique=True)
            # TTL retention based on timestamp, if configured
            from app.core.config import settings
            if getattr(settings, "RETENTION_DAYS", 0) > 0:
                await db.audit_logs.create_index(
                    [("timestamp", 1)],
                    expireAfterSeconds=int(settings.RETENTION_DAYS) * 86400,
                    name="ttl_timestamp",
                )
        except Exception:
            # Index creation failure should not prevent app from starting in dev
            pass


async def close_db():
    global DB_CLIENT
    if DB_CLIENT is not None:
        DB_CLIENT.close()
        DB_CLIENT = None
