from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.deps import get_db
from app.core.auth import require_auth
from app.core.cache import get_redis
from app.core.config import settings
import json
from app.repositories.audit_logs import aggregate_summary, aggregate_timeline
from app.core import circuit


router = APIRouter()


@router.get("/summary", dependencies=[Depends(require_auth)])
async def summary(
    service: Optional[str] = Query(default=None),
    db=Depends(get_db),
):
    # Circuit breaker (optional)
    if circuit.is_open("analytics-db"):
        raise HTTPException(status_code=503, detail="analytics_unavailable")
    # Cache
    cache_key = f"analytics:summary:{service or '*'}"
    r = await get_redis()
    if r is not None:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

    try:
        by_action = await aggregate_summary(db, service)
        total = sum(by_action.values())
        result = {"by_action": by_action, "total": total}
    except Exception as e:
        circuit.record_failure("analytics-db")
        raise HTTPException(status_code=503, detail="analytics_unavailable") from e
    else:
        circuit.record_success("analytics-db")
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
    # Circuit breaker (optional)
    if circuit.is_open("analytics-db"):
        raise HTTPException(status_code=503, detail="analytics_unavailable")
    cache_key = f"analytics:timeline:{service or '*'}:{from_ts or ''}:{to_ts or ''}"
    r = await get_redis()
    if r is not None:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

    try:
        points = await aggregate_timeline(db, service=service, from_ts=from_ts, to_ts=to_ts)
        result = {"points": points}
    except Exception as e:
        circuit.record_failure("analytics-db")
        raise HTTPException(status_code=503, detail="analytics_unavailable") from e
    else:
        circuit.record_success("analytics-db")
    if r is not None:
        await r.setex(cache_key, settings.ANALYTICS_CACHE_TTL, json.dumps(result, default=str))
    return result
