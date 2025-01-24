from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncConnection,
)

from utils import Singleton
from models.base import DeclarativeBaseModel


class DataBaseError(Exception):
    pass


class DatabaseSessionManager(metaclass=Singleton):
    """Синглетон класс для базы данных с поддержкой асинхронности."""

    def __init__(self) -> None:
        self._engine: Optional[AsyncEngine] = None
        self._session_maker: Optional[async_sessionmaker[AsyncSession]] = None

    def init(self, host: str, engine_kwargs, session_kwargs) -> None:
        """Инициализирует соединение с базой данных."""

        engine_kwargs = engine_kwargs if engine_kwargs else {}
        session_kwargs = session_kwargs if session_kwargs else {}

        self._engine = create_async_engine(host, **engine_kwargs)
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            **session_kwargs,
        )

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """Создание асинхронного подключения.

        В качестве контекста возвращает объект `AsyncConnection`.
        В случае возникновения исключения внутри контекста,
        откатывает транзакцию.
        """
        if self._engine is None:
            raise DataBaseError("DatabaseSessionManager is not initialized")
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error("Database connection failed {}", e)
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Создание асинхронной сессии.

        В качестве контекста возвращает объект `AsyncSession`.
        В случае возникновения исключения внутри контекста,
        откатывает транзакцию.
        """
        if self._session_maker is None:
            raise DataBaseError("DatabaseSessionManager is not initialized")
        async with self._session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    async def create_all(self) -> None:
        """(For testing) create all database metadata."""
        async with self._engine.begin() as coon:
            await coon.run_sync(DeclarativeBaseModel.metadata.create_all)

    async def drop_all(self) -> None:
        """(For testing) remove all database metadata."""
        async with self._engine.begin() as coon:
            await coon.run_sync(DeclarativeBaseModel.metadata.drop_all)


db_manager: DatabaseSessionManager = DatabaseSessionManager()


async def get_session() -> AsyncIterator[AsyncSession]:
    """Возвращает сеанс базы данных для использования с fastapi Depends"""
    # noinspection PyArgumentList
    async with db_manager.session() as session:
        yield session
