from typing import Optional

from loguru import logger
from redis import asyncio as aioredis

from app.core.config import settings


_redis: Optional[aioredis.Redis] = None


async def get_redis() -> Optional[aioredis.Redis]:
    global _redis
    if _redis is not None:
        return _redis
    url = getattr(settings, "REDIS_URL", None)
    if not url:
        return None
    try:
        _redis = aioredis.from_url(url, encoding="utf-8", decode_responses=True)
        await _redis.ping()
        logger.info("Redis conectado")
        return _redis
    except Exception as e:  # pragma: no cover
        logger.warning("No se pudo conectar a Redis: {}", e)
        _redis = None
        return None


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None

