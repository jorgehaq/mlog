from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.settings import get_settings
from app.core.database import connect_db
from app.api.v1 import events, analytics, health


settings = get_settings()
app = FastAPI(title=settings.app_name)


origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    logger.remove()
    logger.add(lambda msg: print(msg, end=""))
    logger.info("Starting app: {} (env={})", settings.app_name, settings.app_env)
    await connect_db()


@app.get("/")
async def root():
    return {"app": settings.app_name, "message": "¡Bienvenido a mlog!"}

app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(health.router, prefix="/health", tags=["Health"])
