from core.config import DBSettings
from core.logger import get_logger
from repositories.database.idatabase import IAsyncDatabaseConnection
from sqlalchemy.ext.asyncio import create_async_engine

logger = get_logger(__name__)


class DatabaseConnection(IAsyncDatabaseConnection):
    _engine = None

    def __init__(self, settings: DBSettings):
        self._settings = settings

    async def get_engine(self):
        if self._engine is None:
            self._engine = create_async_engine(self._settings.URI,
                                               echo=self._settings.SQLALCHEMY_ECHO)
        return self._engine

    async def close(self):
        if self._engine:
            await self._engine.dispose()
