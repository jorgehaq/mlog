from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.database import connect_db, close_db
from app.core.cache import close_redis
from app.core.errors import register_exception_handlers
from app.middleware.ratelimit import RateLimitMiddleware
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.metrics import MetricsMiddleware
from prometheus_client import make_asgi_app
from fastapi import APIRouter
from app.core.observability import init_tracing
from app.api.v1 import events, analytics, health


app = FastAPI(title=settings.APP_NAME)


origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(RateLimitMiddleware)


@app.on_event("startup")
async def startup() -> None:
    logger.remove()
    logger.add(lambda msg: print(msg, end=""))
    logger.info("Starting app: {}", settings.APP_NAME)
    await connect_db()
    register_exception_handlers(app)
    init_tracing(app)


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "message": "¡Bienvenido a mlog!"}

app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(health.router, prefix="/health", tags=["Health"])


@app.on_event("shutdown")
async def shutdown() -> None:
    await close_db()
    await close_redis()

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
router_metrics = APIRouter()
router_metrics.add_route("/metrics", endpoint=metrics_app, include_in_schema=False)
app.include_router(router_metrics)
