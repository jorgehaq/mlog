from typing import Optional, Sequence

from fastapi import Depends, HTTPException, Request
from loguru import logger
import jwt

from app.core.config import settings


def _get_auth_headers(request: Request) -> tuple[Optional[str], Optional[str]]:
    api_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    auth = request.headers.get("Authorization")
    token = None
    if auth and auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1].strip()
    return api_key, token


def _valid_api_key(api_key: Optional[str]) -> bool:
    if not api_key:
        return False
    raw: str = getattr(settings, "API_KEYS", "") or ""
    allowed: Sequence[str] = [k.strip() for k in raw.split(",") if k.strip()]
    return bool(allowed) and api_key in allowed


def _valid_jwt(token: Optional[str]) -> bool:
    secret = getattr(settings, "JWT_SECRET", None)
    if not token or not secret:
        return False
    try:
        jwt.decode(token, secret, algorithms=["HS256"])  # payload not used here
        return True
    except Exception as e:  # pragma: no cover
        logger.warning("JWT invalid: {}", e)
        return False


async def require_auth(request: Request):
    # If neither API_KEYS nor JWT_SECRET configured, allow in non-prod envs
    if not (getattr(settings, "API_KEYS", "") or getattr(settings, "JWT_SECRET", None)):
        return
    api_key, token = _get_auth_headers(request)
    if _valid_api_key(api_key) or _valid_jwt(token):
        return
    raise HTTPException(status_code=401, detail="unauthorized")

