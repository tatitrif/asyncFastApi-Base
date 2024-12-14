from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from loguru import logger

from api import routers
from core.config import settings
from core.session_manager import db_manager


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Lifespan event handles startup and shutdown events."""
    logger.info("Start configuring server...")
    db_manager.init(
        settings.SQLALCHEMY_DATABASE_URI,
        {
            "echo": settings.DB_ECHO,
            "future": settings.DB_FUTURE,
            "pool_pre_ping": settings.DB_POOL_PRE_PING,
            "connect_args": settings.DB_CONNECT_ARGS,
        },
        {
            "autoflush": settings.DB_SESSION_AUTOFLUSH,
            "autocommit": settings.DB_SESSION_AUTOCOMMIT,
            "expire_on_commit": settings.DB_SESSION_EXPIRE_ON_COMMIT,
        },
    )

    logger.info("Server started and configured successfully")
    yield
    logger.info("Server shut down")


app = FastAPI(
    title=settings.PROJECT_TITLE,
    description=settings.PROJECT_DESCRIPTION,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    swagger_ui_parameters={
        "filter": True,
    },
)

app.include_router(routers.api_v1_router)
