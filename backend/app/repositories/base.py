from abc import ABC, abstractmethod
from typing import TypeVar, Type, Sequence

from pydantic import BaseModel
from sqlalchemy import insert, select, update, delete, func, RowMapping, Result
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import DeclarativeBaseModel

ModelType = TypeVar("ModelType", bound=DeclarativeBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def find_all(
        self, skip: int | None, limit: int | None, **filter_by
    ) -> list[RowMapping]:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filter_by) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_none(self, **filter_by) -> RowMapping | None:
        raise NotImplementedError

    @abstractmethod
    async def edit_one(self, _id: int, data: dict) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, _id: int) -> RowMapping:
        raise NotImplementedError

    @abstractmethod
    async def count(self, **filter_by) -> int:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    """Этот класс реализует базовый интерфейс для работы с базой данных.
    Упрощает работу с аннотациями типов.
    Поддерживает все классические операции CRUD, а также пользовательские запросы.
    """

    model: Type[ModelType]
    create_schema: Type[CreateSchemaType]
    update_schema: Type[UpdateSchemaType]

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория с помощью сеанса базы данных.

        Args:
            session (AsyncSession): Сеанс базы данных.
        """
        self.session: AsyncSession = session

    async def add_one(self, data: CreateSchemaType) -> Type[ModelType]:
        """Создание объекта

        Args:
            data (CreateSchemaType): Схема вводимых данных.

        Returns:
            Type[ModelType]: экземпляр модель БД.
        """
        stmt = insert(self.model).values(data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def add_many(self, data: list[CreateSchemaType]) -> Sequence[ModelType]:
        stmt = insert(self.model).values(data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_all(self, **filter_dict) -> Sequence[ModelType] | None:
        """Асинхронно находит и возвращает все экземпляры модели,
         удовлетворяющие указанным критериям.

        Args:
            **filter_dict: Критерии фильтрации в виде именованных параметров.

        Returns:
             Список экземпляров модели.
        """
        stmt = select(self.model).filter_by(**filter_dict, is_deleted=0)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_by_page(
        self, limit: int, offset: int = 0, **filter_dict
    ) -> Sequence[ModelType] | None:
        """Асинхронно находит и возвращает все экземпляры модели постранично,
         удовлетворяющие указанным критериям.

        Args:
            offset: Критерии номера страницы,
            limit: Критерии количества объектов на странице.
            **filter_dict: Критерии фильтрации в виде именованных параметров.

        Returns:
            Список экземпляров модели.
        """

        stmt = (
            select(self.model)
            .filter_by(**filter_dict, is_deleted=0)
            .offset((offset - 1) * limit)
            .limit(limit)
        )
        res: Result = await self.session.execute(stmt)
        return res.unique().scalars().all()

    async def find_one(self, **filter_dict) -> Type[ModelType] | None:
        """
        Находит один объект

        Args:
           **filter_dict: Критерии фильтрации в виде именованных параметров.

        Returns:
            Type[ModelType]: экземпляр модель БД.
        """
        stmt = select(self.model).filter_by(**filter_dict, is_deleted=0)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def find_one_or_none(self, **filter_dict) -> Type[ModelType] | None:
        """
        Находит только один объект или ничего

        Args:
           **filter_dict: Критерии фильтрации в виде именованных параметров.

        Returns:
            Type[ModelType]: экземпляр модель БД.
        """
        stmt = select(self.model).filter_by(**filter_dict, is_deleted=0)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def edit_one(self, _id: int, data) -> Type[ModelType]:
        """
        Обновление объекта

        Args:
            _id: объект.
            data:  данные которые нужно обновить.

        Returns:
           Измененный объект
        """
        stmt = update(self.model).values(**data).filter_by(id=_id).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_many(
        self, _ids: list[int], data: UpdateSchemaType
    ) -> Sequence[ModelType]:
        stmt = (
            update(self.model)
            .values(**data)
            .where(self.model.id.in_(_ids))
            .returning(self.model)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def delete_one(self, _id: int) -> Type[ModelType]:
        """
        Удаление объекта

        Args:
            _id: объект.

        Returns:
           Удаленный объект
        """
        stmt = delete(self.model).filter_by(id=_id).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def delete_many(self, **filter_by):
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def count(self, **filter_dict) -> int:
        """
        Подсчет объекта в запросе

        Args:
             **filter_dict: Критерии фильтрации в виде именованных параметров.

        Returns:
           Количество объектов
        """
        stmt = select(func.count(self.model.id)).filter_by(**filter_dict, is_deleted=0)
        res: Result = await self.session.execute(stmt)
        return res.unique().scalars().first()

    async def save(self) -> None:
        self.session.add(self)
        await self.session.commit()
        await self.session.refresh(self)

    async def delete(self) -> None:
        await self.session.delete(self)
        await self.session.commit()
