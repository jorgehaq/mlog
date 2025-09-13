from fastapi import APIRouter
from app.core.database import get_database


router = APIRouter()


@router.get("/")
async def health():
    # Simple check that DB object can be obtained
    try:
        _ = get_database()
        return {"status": "ok"}
    except Exception:
        return {"status": "degraded"}

