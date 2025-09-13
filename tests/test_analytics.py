from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient

from app.main import app
from app.api import deps


class FakeCursor:
    def __init__(self, docs: List[Dict[str, Any]]):
        self._docs = docs
        self._iter = iter(self._docs)

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

    async def insert_one(self, doc: Dict[str, Any]):
        self._docs.append(dict(doc))
        class R:
            inserted_id = str(len(self._docs))
        return R()

    def aggregate(self, pipeline: List[Dict[str, Any]]):
        data = list(self._docs)
        # $match
        match = pipeline[0].get("$match", {}) if pipeline else {}
        for k, v in match.items():
            if isinstance(v, dict) and "$gte" in v or "$lte" in v:
                ts = lambda d: d.get("timestamp")  # noqa: E731
                lo = v.get("$gte")
                hi = v.get("$lte")
                data = [d for d in data if (lo is None or ts(d) >= lo) and (hi is None or ts(d) <= hi)]
            else:
                data = [d for d in data if d.get(k) == v]

        if any("$group" in s for s in pipeline):
            group_stage = next(s["$group"] for s in pipeline if "$group" in s)
            _id = group_stage["_id"]
            if isinstance(_id, str) and _id.startswith("$"):
                key = _id[1:]
                counts: Dict[str, int] = {}
                for d in data:
                    k = d.get(key)
                    counts[k] = counts.get(k, 0) + 1
                out = [{"_id": k, "count": v} for k, v in counts.items()]
            else:
                # dateTrunc by minute
                counts: Dict[datetime, int] = {}
                for d in data:
                    ts = d.get("timestamp")
                    if not isinstance(ts, datetime):
                        continue
                    key_dt = ts.replace(second=0, microsecond=0)
                    counts[key_dt] = counts.get(key_dt, 0) + 1
                out = [{"_id": k, "count": v} for k, v in counts.items()]
            return FakeCursor(out)

        return FakeCursor(data)


class FakeDB:
    def __init__(self) -> None:
        self.audit_logs = FakeCollection()

_FAKE_DB = FakeDB()


def override_get_db():
    return _FAKE_DB


def test_analytics_summary_and_timeline():
    # Inyectar DB falsa
    app.dependency_overrides[deps.get_db] = override_get_db
    client = TestClient(app)

    base = datetime(2025, 1, 1, 0, 0, 0)
    e1 = {"timestamp": base.isoformat() + "Z", "service": "axi", "user_id": "u1", "action": "login", "metadata": {}}
    e2 = {"timestamp": (base + timedelta(seconds=10)).isoformat() + "Z", "service": "axi", "user_id": "u2", "action": "login", "metadata": {}}
    e3 = {"timestamp": (base + timedelta(minutes=1)).isoformat() + "Z", "service": "axi", "user_id": "u3", "action": "purchase", "metadata": {}}
    for e in (e1, e2, e3):
        r = client.post("/events/", json=e)
        assert r.status_code == 200

    rs = client.get("/analytics/summary", params={"service": "axi"})
    assert rs.status_code == 200
    summary = rs.json()
    assert summary["by_action"]["login"] == 2
    assert summary["by_action"]["purchase"] == 1
    assert summary["total"] == 3

    rt = client.get("/analytics/timeline", params={"service": "axi"})
    assert rt.status_code == 200
    timeline = rt.json()
    assert len(timeline["points"]) >= 2
