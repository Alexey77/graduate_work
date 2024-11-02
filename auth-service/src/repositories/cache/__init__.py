from core.config import CacheSettings, cache_settings
from repositories.enums import CacheStorageEnum

from .icache import IAsyncCache
from .redis_cache import RedisRepositories


def cache_factory(settings: CacheSettings, **kwargs) -> IAsyncCache:
    if settings.cache_storage == CacheStorageEnum.REDIS:
        return RedisRepositories(settings=cache_settings)

    raise NotImplementedError(f"No implementation for {settings.cache_storage} in {__name__}.get_cache_storage")