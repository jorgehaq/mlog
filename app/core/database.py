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


async def close_db():
    global DB_CLIENT
    if DB_CLIENT is not None:
        DB_CLIENT.close()
        DB_CLIENT = None
