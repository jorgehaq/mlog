from datetime import datetime
import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.api import deps
from app.core.config import settings


class FakeInsertResult:
    def __init__(self, inserted_id: str) -> None:
        self.inserted_id = inserted_id


class FakeCollection:
    async def insert_one(self, doc):
        return FakeInsertResult("1")


class FakeDB:
    def __init__(self) -> None:
        self.audit_logs = FakeCollection()


def override_get_db():
    return FakeDB()


def test_auth_required_for_events_without_key():
    app.dependency_overrides[deps.get_db] = override_get_db
    # Forzar API_KEYS
    settings.API_KEYS = "secret"
    client = TestClient(app)
    payload = {
        "timestamp": datetime(2025, 1, 1, 0, 0, 0).isoformat() + "Z",
        "service": "axi",
        "user_id": "u1",
        "action": "login",
        "metadata": {},
    }
    r = client.post("/events/", json=payload)
    assert r.status_code == 401


def test_auth_success_with_key():
    app.dependency_overrides[deps.get_db] = override_get_db
    settings.API_KEYS = "secret"
    client = TestClient(app)
    payload = {
        "timestamp": datetime(2025, 1, 1, 0, 0, 0).isoformat() + "Z",
        "service": "axi",
        "user_id": "u1",
        "action": "login",
        "metadata": {},
    }
    r = client.post("/events/", headers={"X-API-Key": "secret"}, json=payload)
    assert r.status_code == 200


def test_auth_success_with_jwt():
    app.dependency_overrides[deps.get_db] = override_get_db
    from app.core.config import settings
    settings.API_KEYS = ""
    settings.JWT_SECRET = "jwtsecret"
    token = jwt.encode({"sub": "u1"}, settings.JWT_SECRET, algorithm="HS256")
    client = TestClient(app)
    payload = {
        "timestamp": datetime(2025, 1, 1, 0, 0, 0).isoformat() + "Z",
        "service": "axi",
        "user_id": "u1",
        "action": "login",
        "metadata": {},
    }
    r = client.post("/events/", headers={"Authorization": f"Bearer {token}"}, json=payload)
    assert r.status_code == 200
