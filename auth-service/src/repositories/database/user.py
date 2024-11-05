from collections.abc import Sequence
from uuid import UUID

from models.entity import (
    Permission,
    ProviderAccount,
    Role,
    User,
    UserRole,
    UserSessions,
)
from repositories.database.idatabase import IAsyncDatabaseConnection, IAsyncUserDatabase
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload

from .exception import DBException


class UserDatabase(IAsyncUserDatabase):
    def __init__(self, db: IAsyncDatabaseConnection):
        self._db = db

    async def _get_engine(self):
        return await self._db.get_engine()

    async def _get_session(self):
        engine = await self._get_engine()
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            yield session

    async def get_active_tokens(self, user_id: UUID) -> Sequence[UserSessions]:
        """Получаем все активные сессии пользователя"""
        async for session in self._get_session():
            query = (
                select(UserSessions)
                .where(UserSessions.user_id == user_id, UserSessions.is_active)
                .order_by(UserSessions.created_at)
            )
            result = await session.execute(query)
            return result.scalars().all()

    async def get_role_by_name(self, role_name: str) -> Role:
        async for session in self._get_session():
            role = await session.execute(select(Role).where(Role.name == role_name))
            return role.scalars().first()

    async def create_user(self, user: User, role: Role) -> User:
        async for session in self._get_session():
            if role := await self.get_role_by_name(role.name):
                try:
                    session.add(user)
                    await session.flush()
                    user_role = UserRole(user_id=user.id, role_id=role.id)
                    session.add(user_role)
                    await session.commit()
                    return user
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise DBException(message=str(e))

    async def authenticate_user(self, login: str, password: str) -> User | None:
        user = await self.get_user_by_login(login)
        if user and user.check_password(password):
            return user
        return None

    async def get_user_by_refresh_token(
        self, refresh_token: str, is_active: bool = False
    ) -> User | None:
        async for session in self._get_session():
            query = (
                select(User)
                .join(UserSessions)
                .where(UserSessions.refresh_token == refresh_token)
            )
            if is_active:
                query = query.where(UserSessions.is_active)
            result = await session.execute(query)
            return result.scalars().first()

    async def get_user_by_login(self, login: str) -> User | None:
        async for session in self._get_session():
            query = select(User).where(User.login == login)
            result = await session.execute(query)
            return result.scalars().first()

    async def get_user_with_provider_accounts(
        self, login: str
    ) -> tuple[User | None, list[ProviderAccount]]:
        async for session in self._get_session():
            query = (
                select(User)
                .options(selectinload(User.provider_accounts))
                .where(User.login == login)
            )
            result = await session.execute(query)
            user = result.scalars().first()
            if user:
                return user, user.provider_accounts
            return None, []

    async def get_user_roles_by_id(self, user_id: UUID) -> Sequence[Role]:
        async for session in self._get_session():
            query = select(Role).join(UserRole).where(UserRole.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().all()

    async def update_user_by_login(self, login: str, **kwargs) -> None:
        async for session in self._get_session():
            query = select(User).where(User.login == login)
            result = await session.execute(query)
            user = result.scalars().first()
            if user:
                for key in User.__table__.columns.keys():  # noqa
                    if key in kwargs:
                        new_value = (
                            User.hash_password(kwargs[key])
                            if key == "password"
                            else kwargs[key]
                        )
                        setattr(user, key, new_value)
                session.add(user)
                await session.commit()

    async def get_user_permissions(self, login: str) -> Sequence[Permission]:
        async for session in self._get_session():
            query = (
                select(Permission.name)
                .join(Role, Permission.roles)
                .join(User, Role.users)
                .where(User.login == login)
            )
            result = await session.execute(query)
            return result.scalars().all()
