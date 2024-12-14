import datetime as datetime
import re

from sqlalchemy import false, Boolean, func, TIMESTAMP, MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    declared_attr,
    DeclarativeBase,
    class_mapper,
)

from core.config import settings
from core.const import NAMING_CONVENTION


class IsDeletedColumn:
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
    )


class UpdatedAtColumn:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        doc="Time of creation",
    )


class CreatedAtColumn:
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        doc="Time of last modification",
    )


class IdColumn:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class DeclarativeBaseModel(AsyncAttrs, DeclarativeBase):
    """Родительский класс всех классов модели данных
    с поддержкой асинхронного доступа к атрибутам.
    Имя таблицы — это название модели, но в змеином регистре.
    """

    @declared_attr
    def __tablename__(self) -> str:
        """Генерация имени таблицы на основе имени класса."""
        # e.g. SomeModelName -> some_model_name
        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.__name__).lower()

    __abstract__ = True

    metadata = MetaData(
        schema=settings.DB_SCHEMA,
        naming_convention=NAMING_CONVENTION,
    )

    repr_cols_num = 3  # print first columns
    repr_cols = ()  # extra printed columns

    def __repr__(self):
        """Строковое представление объекта для удобства отладки."""
        # Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {', '.join(cols)}>"

    def __str__(self):
        return self.__tablename__

    @classmethod
    def from_dict(cls, data: dict):
        """Создаёт объект из словаря."""
        return cls(**data)

    def to_dict(self) -> dict:
        """Преобразует объект в SQLAlchemy словарь."""
        # Получаем mapper для текущей модели
        columns = class_mapper(self.__class__).columns
        # Возвращаем словарь всех колонок и их значений
        return {column.key: getattr(self, column.key) for column in columns}
