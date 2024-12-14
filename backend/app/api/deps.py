from typing import Annotated

from fastapi import Depends

from core import exceptions
from schemas.auth import TokenUserData
from services.helpers.security import oauth2_scheme, get_token_user


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    user = get_token_user(token)
    return user


def get_current_active_user(
    current_user: Annotated[TokenUserData, Depends(get_current_user)],
):
    if current_user.is_deleted:
        raise exceptions.USER_EXCEPTION_INACTIVE_USER
    return current_user


def check_admin_role(
    user: Annotated[TokenUserData, Depends(get_current_active_user)],
):
    if not user.is_superuser:
        raise exceptions.USER_EXCEPTION_PERMISSION_REQUIRED
