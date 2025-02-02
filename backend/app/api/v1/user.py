from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, check_admin_role
from core.session_manager import get_session
from schemas.auth import TokenUserData
from schemas.page import PageResponse, PagedParamsSchema
from schemas.user import UserUpdateSchema, UserFilterSchema, UserResponse
from services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
)
async def read_user_me(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[TokenUserData, Depends(get_current_active_user)],
):
    """
    Данные текущего пользователя.

    Args:
        session: Сессия БД,
        current_user: Текущий пользователь.

    Returns:
        UserResponse: Схема возвращаемых данных о пользователе.
    """
    return await UserService(session).find_one(current_user.id)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user info",
)
async def update_me(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    data: UserUpdateSchema,
):
    """
    Редактирование своих данных.

    Args:
        session: Сессия БД,
        current_user: Текущий пользователь,
        data: Данные для обновления.
    """

    return await UserService(session).edit_me(current_user, data)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user info",
)
async def get_one(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: int,
):
    """
    Возвращает данных пользователя.

    Args:
        session: Сессия БД,
        user_id: Идентификатор пользователя.
    """
    return await UserService(session).find_one(user_id)


@router.get(
    "/",
    response_model=PageResponse,
    summary="View user data by filters",
)
async def get_many(
    session: Annotated[AsyncSession, Depends(get_session, use_cache=True)],
    limit_offset: Annotated[PagedParamsSchema, Depends()],
    filter_schema: Annotated[UserFilterSchema, Depends()],
):
    """
    Возвращает список пользователей.

    Args:
        session: Сессия БД,
        limit_offset: Параметры для постраничного отображения,
        filter_schema: Критерий отбора списка данных.
    """
    return await UserService(session).find_all(limit_offset, filter_schema)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(check_admin_role)],
    summary="Updating user data by Admin",
)
async def update_one_by_id(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: int,
    data: UserUpdateSchema,
):
    """
    Редактирование Админом данных пользователя.

    Args:
        session: Сессия БД,
        user_id: Идентификатор пользователя,
        data: Данные для обновления.
    """
    return await UserService(session).edit_one(user_id, data)


@router.delete(
    "/{user_id}",
    dependencies=[Depends(check_admin_role)],
    summary="Deletion (hiding) of user data by Admin",
)
async def delete_by_id(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: int,
):
    """
    Удаление (скрытие) Админом данных пользователя.

    Args:
        session: Сессия БД,
        user_id: Идентификатор пользователя.
    """
    return await UserService(session).delete_one(user_id)
