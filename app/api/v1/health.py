from fastapi import APIRouter
from app.core.database import get_database
from app.core.database import connect_db


router = APIRouter()


@router.get("/")
async def health():
    # DB ping real
    try:
        await connect_db()
        db = get_database()
        await db.client.admin.command("ping")
        mongo = True
    except Exception:
        mongo = False
    return {"status": "ok" if mongo else "degraded", "mongo": mongo}
