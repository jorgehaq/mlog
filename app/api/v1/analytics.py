from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.deps import get_db
from app.core.auth import require_auth
from app.core.cache import get_redis
from app.core.config import settings
import json


router = APIRouter()


@router.get("/summary", dependencies=[Depends(require_auth)])
async def summary(
    service: Optional[str] = Query(default=None),
    db=Depends(get_db),
):
    # Cache
    cache_key = f"analytics:summary:{service or '*'}"
    r = await get_redis()
    if r is not None:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

    match = {}
    if service:
        match["service"] = service
    pipeline = [
        {"$match": match},
        {"$group": {"_id": "$action", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    try:
        by_action = {}
        async for row in db.audit_logs.aggregate(pipeline):
            by_action[str(row.get("_id"))] = int(row.get("count", 0))
        total = sum(by_action.values())
        result = {"by_action": by_action, "total": total}
    except Exception as e:
        raise HTTPException(status_code=503, detail="analytics_unavailable") from e
    if r is not None:
        await r.setex(cache_key, settings.ANALYTICS_CACHE_TTL, json.dumps(result))
    return result


@router.get("/timeline", dependencies=[Depends(require_auth)])
async def timeline(
    service: Optional[str] = Query(default=None),
    from_ts: Optional[datetime] = Query(default=None),
    to_ts: Optional[datetime] = Query(default=None),
    db=Depends(get_db),
):
    cache_key = f"analytics:timeline:{service or '*'}:{from_ts or ''}:{to_ts or ''}"
    r = await get_redis()
    if r is not None:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

    match = {}
    if service:
        match["service"] = service
    time_filter = {}
    if from_ts:
        time_filter["$gte"] = from_ts
    if to_ts:
        time_filter["$lte"] = to_ts
    if time_filter:
        match["timestamp"] = time_filter
    pipeline = [
        {"$match": match},
        {
            "$group": {
                "_id": {
                    "$dateTrunc": {
                        "date": "$timestamp",
                        "unit": "minute",
                    }
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    try:
        points = []
        async for row in db.audit_logs.aggregate(pipeline):
            ts = row.get("_id")
            points.append({"ts": ts, "count": int(row.get("count", 0))})
        result = {"points": points}
    except Exception as e:
        raise HTTPException(status_code=503, detail="analytics_unavailable") from e
    if r is not None:
        await r.setex(cache_key, settings.ANALYTICS_CACHE_TTL, json.dumps(result, default=str))
    return result
