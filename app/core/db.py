from typing import Optional

from loguru import logger

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except Exception:  # pragma: no cover - motor es opcional para desarrollo
    AsyncIOMotorClient = None  # type: ignore

from app.settings import get_settings


_client: Optional["AsyncIOMotorClient"] = None


async def get_client() -> Optional["AsyncIOMotorClient"]:
    global _client
    if _client is not None:
        return _client
    settings = get_settings()
    mongo_uri = getattr(settings, "mongo_uri", None) or None
    if not mongo_uri:
        logger.warning("MONGO_URI no configurado; usando almacenamiento en memoria.")
        return None
    if AsyncIOMotorClient is None:
        logger.error("motor no instalado; no se puede conectar a MongoDB.")
        return None
    _client = AsyncIOMotorClient(mongo_uri)
    logger.info("Cliente MongoDB inicializado.")
    return _client


async def ping() -> bool:
    client = await get_client()
    if client is None:
        return False
    try:
        await client.admin.command("ping")
        return True
    except Exception as e:  # pragma: no cover
        logger.error("Error ping MongoDB: {}", e)
        return False

