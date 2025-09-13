from typing import Optional

import motor.motor_asyncio
from app.core.config import settings

DB_CLIENT: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None


def get_database():
    global DB_CLIENT
    if DB_CLIENT is None:
        # Lazy init if not connected yet
        DB_CLIENT = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    return DB_CLIENT["mlog"]


async def connect_db():
    global DB_CLIENT
    if DB_CLIENT is None:
        DB_CLIENT = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
