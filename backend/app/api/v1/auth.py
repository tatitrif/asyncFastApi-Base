from typing import Annotated

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from core.session_manager import get_session
from schemas.auth import TokenResponse
from schemas.user import (
    UserCreateSchema,
    UserResponse,
    ValidEmail,
    UserConfirmPasswords,
)
from services.auth import AuthService
from services.helpers.security import OAuth2PasswordAndRefreshRequestForm, oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User registration",
)
async def register_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_data: Annotated[UserCreateSchema, Depends()],
):
    """Регистрация нового пользователя.

    Args:
        session: Сессия БД,
        user_data (UserCreateSchema): Схема данных пользователе для БД.

    Returns:
        UserResponse: Схема данных о пользователе для отображения.
    """
    return await AuthService(session).create_one(user_data)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Authenticate, create tokens, and refresh token",
)
async def login_for_tokens(
    session: Annotated[AsyncSession, Depends(get_session)],
    form_data: Annotated[OAuth2PasswordAndRefreshRequestForm, Depends()],
):
    """Аутентификация, создание токенов и обновление.

    Args:
        session: Сессия БД,
        form_data: Данные аутентификации.
    """
    return await AuthService(session).login(form_data)


@router.post(
    "/logout",
    summary="Logout and removing a token",
)
async def logout(
    session: Annotated[AsyncSession, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    """Выход пользователя из учетной запись и удаление токена.

    Args:
        session: Сессия БД,
        token: Данные токена.
    """
    return await AuthService(session).logout(token)


@router.post(
    "/forgot-password",
)
async def forgot_password(
    session: Annotated[AsyncSession, Depends(get_session)],
    email: Annotated[ValidEmail, Depends()],
):
    return await AuthService(session).forgot_password(email)


@router.post("/reset-password/{token}")
async def reset_password(
    session: Annotated[AsyncSession, Depends(get_session)],
    token: str,
    pwd_data: Annotated[UserConfirmPasswords, Depends()],
):
    """Сброс пароля пользователя"""
    await AuthService(session).reset_password(token, pwd_data)
