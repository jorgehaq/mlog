from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.api import deps


class FakeInsertResult:
    def __init__(self, inserted_id: str) -> None:
        self.inserted_id = inserted_id


class FakeCursor:
    def __init__(self, docs: List[Dict[str, Any]]) -> None:
        self._docs = docs

    def sort(self, key: str, direction: int):  # direction ignored in this fake
        reverse = direction == -1
        self._docs.sort(key=lambda d: d.get(key), reverse=reverse)
        return self

    def limit(self, n: int):
        self._docs = self._docs[:n]
        return self

    def __aiter__(self):
        self._iter = iter(self._docs)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


class FakeCollection:
    def __init__(self) -> None:
        self._docs: List[Dict[str, Any]] = []

    async def insert_one(self, doc: Dict[str, Any]) -> FakeInsertResult:
        _id = str(len(self._docs) + 1)
        stored = dict(doc)
        stored["_id"] = _id
        self._docs.append(stored)
        return FakeInsertResult(_id)

    def find(self, filt: Optional[Dict[str, Any]] = None) -> FakeCursor:
        filt = filt or {}
        service = filt.get("service")
        if service is None:
            matches = list(self._docs)
        else:
            matches = [d for d in self._docs if d.get("service") == service]
        return FakeCursor(matches)

    def aggregate(self, pipeline: List[Dict[str, Any]]):
        # Not used in these tests
        raise NotImplementedError


class FakeDB:
    def __init__(self) -> None:
        self.audit_logs = FakeCollection()


_FAKE_DB = FakeDB()


def override_get_db():
    return _FAKE_DB


def test_create_and_list_events():
    # Ensure auth disabled for this test
    settings.API_KEYS = ""
    app.dependency_overrides[deps.get_db] = override_get_db
    with TestClient(app) as client:
        payload = {
            "timestamp": datetime(2025, 1, 1, 0, 0, 0).isoformat() + "Z",
            "service": "axi",
            "user_id": "u1",
            "action": "login",
            "metadata": {"ip": "127.0.0.1"},
        }

        r1 = client.post("/events/", json=payload)
        assert r1.status_code == 200, r1.text
        data = r1.json()
        assert data["id"]
        assert data["service"] == "axi"
        assert data["action"] == "login"

        r2 = client.get("/events/axi")
        assert r2.status_code == 200, r2.text
        payload2 = r2.json()
        assert isinstance(payload2, dict)
        assert isinstance(payload2.get("items"), list)
        assert len(payload2["items"]) == 1
        assert payload2["items"][0]["service"] == "axi"
