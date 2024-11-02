from uuid import UUID

from core.logger import get_logger
from models.entity import UserSessions
from repositories.database.idatabase import (IAsyncDatabaseConnection,
                                             IAsyncSessionDatabase)
from schemas import ResponseUserHistory, UserHistoryItem
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = get_logger(__name__)


class SessionDatabase(IAsyncSessionDatabase):

    def __init__(self, db: IAsyncDatabaseConnection):
        self._db = db

    async def _get_engine(self):
        return await self._db.get_engine()

    async def _get_session(self):
        engine = await self._get_engine()
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            yield session

    async def add_user_session(self,
                               user_id: UUID,
                               refresh_token: str,
                               **kwargs) -> bool:
        async for session in self._get_session():
            user_session = UserSessions(refresh_token=refresh_token,
                                        user_id=user_id,
                                        user_agent=kwargs.get("user_agent"))
            session.add(user_session)
            await session.commit()
            return True
        return False

    async def delete_session(self, refresh_token: str) -> None:
        async for session in self._get_session():
            query = delete(UserSessions).where(UserSessions.refresh_token == refresh_token)
            await session.execute(query)
            await session.commit()

    async def delete_all_sessions_by_user_id(self, user_id: UUID) -> int:
        async for session in self._get_session():
            query = delete(UserSessions).where(UserSessions.user_id == user_id)
            result = await session.execute(query)
            await session.commit()
            return result.rowcount

    async def get_user_sessions_by_user_id(self, user_id: UUID) -> ResponseUserHistory:
        async for session in self._get_session():
            try:

                query = select(UserSessions). \
                    where(UserSessions.user_id == user_id). \
                    order_by(UserSessions.updated_at.desc())

                result = await session.execute(query)
                sessions = result.scalars().all()
                history = [UserHistoryItem(user_agent=session.user_agent,
                                           time=session.updated_at) for session in sessions]
                return ResponseUserHistory(history=history)
            except SQLAlchemyError as e:
                logger.error(f"Failed to fetch user history: {e}")
                raise
