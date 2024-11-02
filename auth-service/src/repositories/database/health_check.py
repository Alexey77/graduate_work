from core.logger import get_logger
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import async_sessionmaker

from .idatabase import IAsyncDatabaseConnection

logger = get_logger(__name__)


class HealthCheckDB:
    def __init__(self, connection: IAsyncDatabaseConnection):
        self._db = connection

    async def _get_engine(self):
        return await self._db.get_engine()

    async def _get_session(self):
        engine = await self._get_engine()
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            yield session

    async def check_database(self) -> bool:
        try:
            async for session in self._get_session():
                await session.execute(text("SELECT 1"))
            return True
        except OperationalError as e:
            logger.error(f"{e}")
            return False
