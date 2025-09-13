from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.settings import get_settings
from app.api.v1.router import router as api_router


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
async def on_startup() -> None:
    logger.remove()
    logger.add(lambda msg: print(msg, end=""))
    logger.info("Starting app: {} (env={})", settings.app_name, settings.app_env)


@app.get("/")
async def root():
    return {"app": settings.app_name, "message": "¡Bienvenido a mlog!"}

app.include_router(api_router, prefix="")
