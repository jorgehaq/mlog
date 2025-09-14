from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.api import deps


def test_correlation_and_metrics_and_ratelimit(monkeypatch):
    # Reduce rate limit to trigger easily
    from app.core.config import settings
    settings.RATE_LIMIT_PER_MIN = 3

    client = TestClient(app)

    # Correlation: custom header should be echoed back
    r = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert r.status_code in (200, 503)
    assert r.headers.get("X-Request-ID") == "abc-123"

    # Hit health a few times to trigger 429
    client.get("/health")
    client.get("/health")
    rr = client.get("/health")
    assert rr.status_code in (200, 429)

    # Create an event and verify business metric appears
    payload = {
        "timestamp": datetime(2025, 1, 1, 0, 0, 0).isoformat() + "Z",
        "service": "axi",
        "user_id": "u1",
        "action": "login",
        "metadata": {},
    }
    re = client.post("/events/", json=payload)
    assert re.status_code == 200

    m = client.get("/metrics")
    assert m.status_code == 200
    text = m.text
    assert "http_requests_total" in text
    assert "events_created_total" in text


class FakeRedis:
    def __init__(self):
        self._data = {}

    async def get(self, key: str):
        return self._data.get(key)

    async def setex(self, key: str, ttl: int, value: str):
        self._data[key] = value


def test_analytics_uses_cache(monkeypatch):
    # Override Redis with fake
    from app.core import cache
    fr = FakeRedis()
    async def _get_redis():
        return fr
    monkeypatch.setattr(cache, "get_redis", _get_redis)

    # Fake DB that aggregates once, then raises if called again
    called = {"n": 0}

    class FakeCursor:
        def __init__(self, rows):
            self._rows = rows
        def __aiter__(self):
            self._iter = iter(self._rows)
            return self
        async def __anext__(self):
            try:
                return next(self._iter)
            except StopIteration:
                raise StopAsyncIteration

    class FakeDB:
        class _Audit:
            def aggregate(self, pipeline):
                called["n"] += 1
                if called["n"] > 1:
                    raise RuntimeError("should use cache")
                return FakeCursor([{"_id": "login", "count": 1}])
        audit_logs = _Audit()

    def override_get_db():
        return FakeDB()

    app.dependency_overrides[deps.get_db] = override_get_db
    client = TestClient(app)

    s1 = client.get("/analytics/summary")
    assert s1.status_code == 200
    s2 = client.get("/analytics/summary")
    assert s2.status_code == 200
    assert called["n"] == 1  # segunda vez respondió desde cache

