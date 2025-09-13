from fastapi import APIRouter


router = APIRouter()


@router.get("/summary")
async def summary():
    # Placeholder básico; integrar agregaciones más adelante
    return {"by_action": {}, "total": 0}


@router.get("/timeline")
async def timeline():
    # Placeholder básico; integrar agregaciones más adelante
    return {"points": []}

