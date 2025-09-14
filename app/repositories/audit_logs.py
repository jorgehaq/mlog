from datetime import datetime
from typing import Any, Dict, List, Optional


async def aggregate_summary(db: Any, service: Optional[str] = None) -> Dict[str, int]:
    match: Dict[str, Any] = {}
    if service:
        match["service"] = service
    pipeline = [
        {"$match": match},
        {"$group": {"_id": "$action", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    by_action: Dict[str, int] = {}
    async for row in db.audit_logs.aggregate(pipeline):
        by_action[str(row.get("_id"))] = int(row.get("count", 0))
    return by_action


async def aggregate_timeline(
    db: Any,
    *,
    service: Optional[str] = None,
    from_ts: Optional[datetime] = None,
    to_ts: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    match: Dict[str, Any] = {}
    if service:
        match["service"] = service
    time_filter: Dict[str, Any] = {}
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
    points: List[Dict[str, Any]] = []
    async for row in db.audit_logs.aggregate(pipeline):
        ts = row.get("_id")
        points.append({"ts": ts, "count": int(row.get("count", 0))})
    return points

