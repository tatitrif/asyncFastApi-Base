from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl
from pydantic_settings import SettingsConfigDict, BaseSettings

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured with environment variables.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # FastAPI
    PROJECT_TITLE: str = "Project Name"
    PROJECT_DESCRIPTION: str = "Fastapi project description"
    VERSION: str = "0.0.1"
    API_V1_STR: str = "/api/v1"

    # db
    DB_SCHEMA: str | None = None
    DB_ECHO: bool = False
    DB_FUTURE: bool = True
    DB_POOL_PRE_PING: bool = True
    DB_SESSION_AUTOFLUSH: bool = False
    DB_SESSION_AUTOCOMMIT: bool = False
    DB_SESSION_EXPIRE_ON_COMMIT: bool = False
    DB_CONNECT_ARGS: dict = {}

    SQLITE_FILENAME: str = "db_project"
    SQLITE_DATABASE_URI: str = f"sqlite+aiosqlite:///./{SQLITE_FILENAME}.db"
    SQLALCHEMY_DATABASE_URI: str = SQLITE_DATABASE_URI

    # auth
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 2
    REFRESH_TOKEN_EXPIRE_HOURS: int = 24 * 2

    # Email
    EMAIL_FROM: str = ""
    EMAIL_PASSWORD: str = ""
    SMTP_SERVER: str = ""
    FORGET_PASSWORD_LINK_EXPIRE_MINUTES: int = 10

    # JSON-formatted list of origins
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Redis
    REDIS_HOST: str = ""
    REDIS_PASSWORD: str | None = None
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # cache
    CACHE_EXPIRE_SEC: int = 60 * 2

    CELERY_BROKER_URL: str = ""


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
