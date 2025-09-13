import os
from typing import Optional

import motor.motor_asyncio

DB_CLIENT: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None


def get_database():
    global DB_CLIENT
    if DB_CLIENT is None:
        # Lazy init if not connected yet
        MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        DB_CLIENT = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    return DB_CLIENT["mlog"]


async def connect_db():
    global DB_CLIENT
    if DB_CLIENT is None:
        MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        DB_CLIENT = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

