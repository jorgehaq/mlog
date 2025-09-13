#!/usr/bin/env python3
"""
Exporta eventos desde MongoDB a NDJSON para BigQuery.

Uso:
  python scripts/bq_export.py --service axi --from 2025-01-01T00:00:00Z --to 2025-01-02T00:00:00Z --out events.ndjson

Variables de entorno: MONGO_URI
"""
import argparse
import asyncio
import json
import os
from datetime import datetime

import motor.motor_asyncio


def parse_dt(s: str | None):
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service")
    parser.add_argument("--from", dest="from_ts")
    parser.add_argument("--to", dest="to_ts")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    db = client["mlog"]

    q = {}
    if args.service:
        q["service"] = args.service
    time_filter = {}
    f = parse_dt(args.from_ts)
    t = parse_dt(args.to_ts)
    if f:
        time_filter["$gte"] = f
    if t:
        time_filter["$lte"] = t
    if time_filter:
        q["timestamp"] = time_filter

    count = 0
    with open(args.out, "w", encoding="utf-8") as fp:
        async for doc in db.audit_logs.find(q).sort("timestamp", 1):
            doc["_id"] = str(doc.get("_id"))
            fp.write(json.dumps(doc, default=str) + "\n")
            count += 1
    print(f"Exported {count} documents to {args.out}")


if __name__ == "__main__":
    asyncio.run(main())

