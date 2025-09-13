from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "mlog"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    # Comma-separated list
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    mongo_uri: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name="mlog",
    )
