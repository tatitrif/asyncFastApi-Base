import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    # time in seconds it took to process the request and generate the response
    response.headers["X-Process-Time"] = str(time.time() - start_time)
    return response


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # custom headers that client in a browser to be able to see
        expose_headers=["X-Process-Time"],
    )

app.include_router(routers.api_v1_router)
