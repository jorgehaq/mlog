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
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_MIN_POOL_SIZE: int = int(os.getenv("DB_MIN_POOL_SIZE", 0))
    DB_MAX_POOL_SIZE: int = int(os.getenv("DB_MAX_POOL_SIZE", 100))


settings = Settings()
