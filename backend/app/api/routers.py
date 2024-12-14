"""FastAPI route definitions."""

from fastapi import APIRouter

from core.config import settings
from .v1 import health, auth, user

api_v1_router = APIRouter(prefix=settings.API_V1_STR)

api_v1_router.include_router(user.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(health.router)
