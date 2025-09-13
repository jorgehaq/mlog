from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from app.api.deps import get_db


router = APIRouter()


@router.get("/summary")
async def summary(
    service: Optional[str] = Query(default=None),
    db=Depends(get_db),
):
    match = {}
    if service:
        match["service"] = service
    pipeline = [
        {"$match": match},
        {"$group": {"_id": "$action", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    by_action = {}
    async for row in db.audit_logs.aggregate(pipeline):
        by_action[str(row.get("_id"))] = int(row.get("count", 0))
    total = sum(by_action.values())
    return {"by_action": by_action, "total": total}


@router.get("/timeline")
async def timeline(
    service: Optional[str] = Query(default=None),
    from_ts: Optional[datetime] = Query(default=None),
    to_ts: Optional[datetime] = Query(default=None),
    db=Depends(get_db),
):
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
    points = []
    async for row in db.audit_logs.aggregate(pipeline):
        ts = row.get("_id")
        points.append({"ts": ts, "count": int(row.get("count", 0))})
    return {"points": points}
