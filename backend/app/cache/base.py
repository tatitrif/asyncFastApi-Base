from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class AbstractCache(ABC):
    """Абстрактный класс для реализации кеша данных."""

    @abstractmethod
    async def get(self, key: str) -> SchemaType | None:
        """Получает значение из кеша по ключу."""
        pass

    @abstractmethod
    async def set(self, key: str, value: SchemaType, timeout: int) -> None:
        """Записывает значение в кеш по ключу и устанавливает таймаут для удаления."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Удаляет значение из кеша по ключу."""
        pass

    @abstractmethod
    async def delete_namespace(self, prefix: str) -> None:
        """Удаляет все ключи с указанным префиксом."""
        pass
