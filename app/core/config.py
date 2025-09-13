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
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    PORT: int = int(os.getenv("PORT", 8000))


settings = Settings()

