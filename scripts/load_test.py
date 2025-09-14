#!/usr/bin/env python3
"""
Pequeño generador de carga para endpoints del backend usando httpx.

Uso:
  python scripts/load_test.py --rps 50 --duration 30 --base http://localhost:8000 --api-key secret
"""
import argparse
import asyncio
import time
from typing import Optional

import httpx


async def worker(base: str, stop_at: float, api_key: Optional[str]) -> int:
    headers = {"X-API-Key": api_key} if api_key else {}
    done = 0
    async with httpx.AsyncClient(base_url=base, timeout=5) as client:
        while time.time() < stop_at:
            try:
                await client.get("/health", headers=headers)
                done += 1
            except Exception:
                pass
    return done


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rps", type=int, default=10)
    p.add_argument("--duration", type=int, default=30)
    p.add_argument("--base", default="http://localhost:8000")
    p.add_argument("--api-key")
    args = p.parse_args()

    # Aproximar RPS con N workers
    workers = max(1, args.rps // 5)
    stop_at = time.time() + args.duration
    totals = await asyncio.gather(*(worker(args.base, stop_at, args.api_key) for _ in range(workers)))
    print({"requests": sum(totals), "workers": workers, "duration": args.duration})


if __name__ == "__main__":
    asyncio.run(main())

