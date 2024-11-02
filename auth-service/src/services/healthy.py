from functools import lru_cache

from dependencies import get_cache, get_db_connection
from fastapi import Depends
from repositories.cache.health_check import HealthCheckRedis
from repositories.cache.icache import IAsyncCache
from repositories.database.health_check import HealthCheckDB
from repositories.database.idatabase import IAsyncDatabaseConnection


class HealthCheckService:
    def __init__(self,
                 cache: IAsyncCache,
                 db: IAsyncDatabaseConnection,

                 ):
        self._cache = HealthCheckRedis(cache)
        self._db = HealthCheckDB(connection=db)

    async def check_database(self) -> bool:
        return await self._db.check_database()

    async def check_cache(self) -> bool:
        return await self._cache.check_cache()


@lru_cache()
def get_health_check_service(
        cache: IAsyncCache = Depends(get_cache),
        db: IAsyncDatabaseConnection = Depends(get_db_connection),
) -> HealthCheckService:
    return HealthCheckService(cache, db)
