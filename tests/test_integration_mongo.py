import os
import pytest


pytestmark = pytest.mark.asyncio


async def test_mongo_ping_integration():
    uri = os.getenv("MONGO_URI")
    if not uri:
        pytest.skip("MONGO_URI not set")
    try:
        import motor.motor_asyncio as mtr
    except Exception:
        pytest.skip("motor not available")

    client = mtr.AsyncIOMotorClient(uri, serverSelectionTimeoutMS=500)
    try:
        await client.admin.command("ping")
    except Exception:
        pytest.skip("Mongo not reachable")
