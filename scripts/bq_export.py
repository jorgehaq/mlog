#!/usr/bin/env python3
"""
Exporta eventos desde MongoDB a NDJSON y opcionalmente sube a GCS y carga a BigQuery.

Uso:
  python scripts/bq_export.py --service axi --from 2025-01-01T00:00:00Z --to 2025-01-02T00:00:00Z --out events.ndjson \
    [--gcs-bucket my-bucket --gcs-path exports/events.ndjson] [--bq-dataset my_ds --bq-table audit_logs]

Variables de entorno: MONGO_URI, GOOGLE_APPLICATION_CREDENTIALS (para GCP)
"""
import argparse
import asyncio
import json
import os
from datetime import datetime

import motor.motor_asyncio

try:
    from google.cloud import storage  # type: ignore
    from google.cloud import bigquery  # type: ignore
except Exception:  # pragma: no cover
    storage = None
    bigquery = None


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
    parser.add_argument("--gcs-bucket")
    parser.add_argument("--gcs-path")
    parser.add_argument("--bq-dataset")
    parser.add_argument("--bq-table")
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

    # Optional: upload to GCS
    if args.gcs_bucket and args.gcs_path:
        if storage is None:
            raise RuntimeError("google-cloud-storage no instalado")
        cli = storage.Client()
        bucket = cli.bucket(args.gcs_bucket)
        blob = bucket.blob(args.gcs_path)
        blob.upload_from_filename(args.out, content_type="application/x-ndjson")
        print(f"Uploaded to gs://{args.gcs_bucket}/{args.gcs_path}")

    # Optional: load into BigQuery
    if args.bq_dataset and args.bq_table and args.gcs_bucket and args.gcs_path:
        if bigquery is None:
            raise RuntimeError("google-cloud-bigquery no instalado")
        bq = bigquery.Client()
        uri = f"gs://{args.gcs_bucket}/{args.gcs_path}"
        dataset_ref = bq.dataset(args.bq_dataset)
        table_ref = dataset_ref.table(args.bq_table)
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON, autodetect=True, write_disposition="WRITE_APPEND"
        )
        load_job = bq.load_table_from_uri(uri, table_ref, job_config=job_config)
        load_job.result()
        print(f"Loaded into {args.bq_dataset}.{args.bq_table}")


if __name__ == "__main__":
    asyncio.run(main())
