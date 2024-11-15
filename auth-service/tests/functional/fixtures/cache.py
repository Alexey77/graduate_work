import aioredis
import pytest_asyncio

from functional.settings import cache_settings


@pytest_asyncio.fixture(name='redis_pool')
async def redis_pool():
    pool = await aioredis.create_redis_pool(
        (cache_settings.redis_host, cache_settings.redis_port), minsize=5, maxsize=10,
    )
    yield pool
    pool.close()
    await pool.wait_closed()


@pytest_asyncio.fixture(name='redis_get')
async def redis_get(redis_pool):
    async def inner(redis_key):
        cached_result = None
        cached_result = await redis_pool.get(redis_key)
        return cached_result

    return inner


@pytest_asyncio.fixture(name='redis_del')
async def redis_del(redis_pool):
    async def inner(redis_key):
        await redis_pool.delete(redis_key)

    return inner
