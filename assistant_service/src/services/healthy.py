from functools import lru_cache

# from dependencies import get_db


class HealthCheckService:
    def __init__(
        self,
        # db
    ) -> None:
        pass
        # self._db = db

    async def check_db(self) -> bool:
        pass


@lru_cache
def get_health_check_service(
    # db=Depends(get_db)
) -> HealthCheckService:
    return HealthCheckService(
        # db
    )
