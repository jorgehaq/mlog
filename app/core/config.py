from dotenv import load_dotenv
import os
from pathlib import Path

# Load correct .env file based on ENV variable
ENV = os.getenv("ENV", "local")
ENV_PATH = Path(f".env.{ENV}")
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()


def _get_env_or_file(key: str, default: str | None = None) -> str | None:
    file_key = f"{key}_FILE"
    file_path = os.getenv(file_key)
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return os.getenv(key, default)


class Settings:
    # App
    APP_NAME: str = os.getenv("APP_NAME", "mlog")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    PORT: int = int(os.getenv("PORT", 8000))
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080",
    )

    # Database
    MONGO_URI: str = _get_env_or_file("MONGO_URI", "mongodb://localhost:27017") or "mongodb://localhost:27017"
    DB_MIN_POOL_SIZE: int = int(os.getenv("DB_MIN_POOL_SIZE", 0))
    DB_MAX_POOL_SIZE: int = int(os.getenv("DB_MAX_POOL_SIZE", 100))

    # Security
    API_KEYS: str = _get_env_or_file("API_KEYS", "") or ""  # comma-separated keys
    JWT_SECRET: str | None = _get_env_or_file("JWT_SECRET")
    RATE_LIMIT_PER_MIN: int = int(os.getenv("RATE_LIMIT_PER_MIN", 60))
    ENV: str = os.getenv("ENV", "local")
    REDIS_URL: str | None = os.getenv("REDIS_URL")
    ANALYTICS_CACHE_TTL: int = int(os.getenv("ANALYTICS_CACHE_TTL", 30))


settings = Settings()
