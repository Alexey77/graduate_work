from core.logger import get_logger
from redis.exceptions import RedisError
from repositories.cache.icache import IAsyncCache

logger = get_logger(__name__)


class HealthCheckRedis:
    def __init__(self, cache: IAsyncCache):
        self._cache = cache

    async def check_cache(self) -> bool:
        try:
            await self._cache.set("healthcheck_key", "1", ex=10)
            value = await self._cache.get("healthcheck_key")
            if value == "1":
                return True
            return False
        except RedisError as e:
            logger.error(f"Redis error: {e}")
            return False
