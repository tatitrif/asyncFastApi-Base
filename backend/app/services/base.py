from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.base import SQLAlchemyRepository

RepositoryType = TypeVar("RepositoryType", bound=SQLAlchemyRepository)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class AbstractService(ABC):
    """Abstract class to be used as a parent class for all services, defining the
    methods that each service should implement."""

    @abstractmethod
    def find_all(self):
        """Get all objects from the table."""
        pass

    @abstractmethod
    def find_one(self, object_id):
        """Get an object from the repository that is represented by the service, by
        ID."""
        pass

    @abstractmethod
    def create_one(self, obj):
        """Create a new object on the repository that is represented by the service."""
        pass

    @abstractmethod
    def edit_one(self, object_id: int, obj):
        """Update an object on the repository that is represented by the service."""
        pass

    @abstractmethod
    def delete_one(self, object_id: int):
        """Delete an object from the repository."""
        pass


class QueryService(ABC):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    repository: SQLAlchemyRepository
