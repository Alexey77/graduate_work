from datetime import datetime
from typing import Any, Callable

import redis.asyncio as aioredis
from core.config import settings


def _generate_request_key(user_id: str) -> str:
    return f'{user_id}:{datetime.now().minute}'


async def track_request_with_redis(user_id: str, client: aioredis.Redis, ttl: int = settings.RATE_LIMIT_TTL) -> int:
    pipe = client.pipeline()
    key = _generate_request_key(user_id=user_id)
    await pipe.incr(key, 1)
    await pipe.expire(key, ttl)

    result = await pipe.execute()

    return result[0]


def get_track_request(client: Any) -> Callable:
    if isinstance(client, aioredis.Redis):
        return track_request_with_redis

    raise NotImplementedError("Unsupported caching client")
