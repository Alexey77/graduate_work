from core.config import CacheSettings
from core.logger import get_logger
from redis.asyncio import Redis
from redis.exceptions import RedisError
from repositories.cache.icache import IAsyncCache

logger = get_logger(__name__)


class RedisConnectionError(Exception):
    def __init__(self, message="Error connecting to Redis"):
        self.message = message
        super().__init__(self.message)


class RedisRepositories(IAsyncCache):
    def __init__(self, settings: CacheSettings):
        self._settings = settings
        self._client = Redis(
            host=self._settings.host, port=self._settings.port, decode_responses=True
        )

    @property
    def client(self):
        return self._client

    async def delete(self, key: str) -> bool:
        try:
            result = await self._client.delete(key)
            return result > 0
        except RedisError as e:
            logger.error(e)

            return False

    async def get(self, key: str) -> str | None:
        try:
            return await self._client.get(key)
        except RedisError as e:
            logger.error(e)
            return None

    async def set(self, key: str, value: str, **kwargs) -> bool:
        if self._settings.expiration_time > 0:
            return await self._client.set(key, value, self._settings.expiration_time)
        else:
            return await self._client.set(key, value)

    async def close(self) -> None:
        await self._client.close()
