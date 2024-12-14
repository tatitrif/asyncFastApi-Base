from sqlalchemy import false, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import (
    DeclarativeBaseModel,
    IsDeletedColumn,
    UpdatedAtColumn,
    CreatedAtColumn,
    IdColumn,
)


class User(
    DeclarativeBaseModel, IdColumn, IsDeletedColumn, UpdatedAtColumn, CreatedAtColumn
):
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    fullname: Mapped[str] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false()
    )
    image: Mapped[str] = mapped_column(String(255), nullable=True)
