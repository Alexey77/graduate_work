from core.config import DBSettings, db_settings
from repositories.database.idatabase import IAsyncDatabaseConnection
from repositories.enums import DBStorageEnum

from .connection import DatabaseConnection


def db_factory(settings: DBSettings, **kwargs) -> IAsyncDatabaseConnection:
    if (
        settings.db_storage == DBStorageEnum.SQLITE
        or settings.db_storage == DBStorageEnum.POSTGRESQL
    ):
        return DatabaseConnection(settings=db_settings)

    exc_msg = f"No implementation for {settings.db_storage} in {__name__}.db_factory"
    raise NotImplementedError(exc_msg)
