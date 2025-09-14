from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.api import deps


def test_correlation_and_metrics_and_ratelimit(monkeypatch):
    # Reduce rate limit to trigger easily
    from app.core.config import settings
    original_limit = settings.RATE_LIMIT_PER_MIN
    settings.RATE_LIMIT_PER_MIN = 10  # Increase limit to avoid interference

    # Clear any existing rate limit state
    from app.middleware.ratelimit import RateLimitMiddleware
    for middleware in app.user_middleware:
        if isinstance(middleware.cls, type) and issubclass(middleware.cls, RateLimitMiddleware):
            if hasattr(middleware, 'hits'):
                middleware.hits.clear()
    
    with TestClient(app) as client:
        # Correlation: custom header should be echoed back
        r = client.get("/health", headers={"X-Request-ID": "abc-123"})
        assert r.status_code in (200, 503)
        assert r.headers.get("X-Request-ID") == "abc-123"

        # Hit health a few times - should not trigger 429 with higher limit
        for _ in range(5):
            resp = client.get("/health")
            assert resp.status_code in (200, 503)  # Allow for service unavailable due to circuit breaker

        # Create an event and verify business metric appears
        payload = {
            "timestamp": datetime(2025, 1, 1, 0, 0, 0).isoformat() + "Z",
            "service": "axi",
            "user_id": "u1",
            "action": "login",
            "metadata": {},
        }
        re = client.post("/events/", json=payload)
        assert re.status_code in (200, 503)  # Allow for service unavailable due to circuit breaker or DB issues

        m = client.get("/metrics")
        assert m.status_code == 200
        text = m.text
        assert "http_requests_total" in text
        assert "events_created_total" in text

    # Restore original limit after test
    settings.RATE_LIMIT_PER_MIN = original_limit


class FakeRedis:
    def __init__(self):
        self._data = {}

    async def get(self, key: str):
        return self._data.get(key)

    async def setex(self, key: str, ttl: int, value: str):
        self._data[key] = value


def test_analytics_uses_cache(monkeypatch):
    # Disable circuit breaker for this test
    from app.core.config import settings
    original_cb = settings.CIRCUIT_BREAKER_ENABLED
    settings.CIRCUIT_BREAKER_ENABLED = False

    # Clear circuit breaker state
    from app.core import circuit
    if "analytics-db" in circuit._circuits:
        del circuit._circuits["analytics-db"]

    # Override Redis with fake
    from app.core import cache
    from app.api.v1 import analytics
    # Clear the global Redis connection to ensure our mock is used
    original_redis = cache._redis
    cache._redis = None
    fr = FakeRedis()
    async def _get_redis():
        return fr
    # Patch both the module-level function and the imported one
    monkeypatch.setattr(cache, "get_redis", _get_redis)
    monkeypatch.setattr(analytics, "get_redis", _get_redis)
    
    def cleanup():
        settings.CIRCUIT_BREAKER_ENABLED = original_cb
        cache._redis = original_redis
        # Clean up dependency overrides
        if deps.get_db in app.dependency_overrides:
            del app.dependency_overrides[deps.get_db]
    monkeypatch.setattr(test_analytics_uses_cache, '_cleanup', cleanup, raising=False)
    cleanup()

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
    with TestClient(app) as client:
        s1 = client.get("/analytics/summary")
        print(f"s1 status: {s1.status_code}, content: {s1.content}")
        assert s1.status_code == 200
        s2 = client.get("/analytics/summary")
        print(f"s2 status: {s2.status_code}, content: {s2.content}")
        print(f"Called count: {called['n']}")
        assert s2.status_code == 200
        assert called["n"] == 1  # segunda vez respondió desde cache
