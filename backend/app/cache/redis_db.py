import orjson
from loguru import logger
from redis.asyncio import Redis, ConnectionPool

from utils import singleton
from .base import AbstractCache, SchemaType


@singleton
class RedisCache(AbstractCache):
    """Кэш данных в Redis."""

    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        password: str | None = None,
        max_connections: int = 5,
    ) -> None:
        self._pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=2,
            socket_connect_timeout=2,
            max_connections=max_connections,
        )
        self._redis = Redis(connection_pool=self._pool)

    async def get(self, key: str) -> SchemaType | None:
        logger.debug(f"Get from cache {key}", key=key)

        value = await self._redis.get(key)
        if value is not None:
            return orjson.loads(value)
        return None

    async def set(self, key: str, value: SchemaType, expire: int) -> None:
        logger.debug(f"Set to cache {key}", key=key)

        if isinstance(value, list):
            data = [_.model_dump() for _ in value]
        else:
            data = value.model_dump()

        if isinstance(data, dict) or isinstance(data, list):
            data = orjson.dumps(data)

        await self._redis.set(key, data, ex=expire)

    async def delete(self, key: str) -> None:
        logger.debug(f"Delete_ from cache {key}", key=key)
        await self._redis.delete(key)

    async def clear(self) -> None:
        logger.debug("Clear cache")
        await self._redis.flushdb(asynchronous=True)

    async def delete_namespace(self, prefix: str) -> None:
        logger.debug(f"Delete namespace from cache {prefix}", prefix=prefix)
        async for key in self._redis.scan_iter(f"{prefix}*"):
            await self._redis.delete(key)
