from core.logger import get_logger
from models.entity import ProviderAccount, User
from repositories.database.idatabase import IAsyncDatabaseConnection
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker

from .idatabase import IProviderDatabase

logger = get_logger(__name__)


class ProviderDatabase(IProviderDatabase):
    def __init__(self, db: IAsyncDatabaseConnection):
        self._db = db

    async def _get_engine(self):
        return await self._db.get_engine()

    async def _get_session(self):
        engine = await self._get_engine()
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            yield session

    async def add_provider_account(
        self, provider_account: ProviderAccount
    ) -> ProviderAccount:
        async for session in self._get_session():
            session.add(provider_account)
            try:
                await session.commit()
                return provider_account
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Error adding a provider: {e}")
                raise

    async def get_provider_account_by_login(
        self, login: str, provider_name: str
    ) -> ProviderAccount | None:
        async for session in self._get_session():
            query = (
                select(ProviderAccount)
                .join(User)
                .where(
                    User.login == login, ProviderAccount.provider_name == provider_name
                )
            )
            result = await session.execute(query)
            return result.scalars().first()
