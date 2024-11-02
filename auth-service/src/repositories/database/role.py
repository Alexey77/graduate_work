from models.entity import Role, User, UserRole
from repositories.database.idatabase import (IAsyncDatabaseConnection,
                                             IAsyncRoleDatabase)
from schemas import Role as RoleSchemas
from services.exception import RoleException
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker


class RoleDatabase(IAsyncRoleDatabase):

    def __init__(self, db: IAsyncDatabaseConnection):
        self._db = db

    async def _get_engine(self):
        return await self._db.get_engine()

    async def _get_session(self):
        engine = await self._get_engine()
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            yield session

    async def create_role(self, role: RoleSchemas) -> Role:
        role = Role(name=role.name, description=role.description)
        async for session in self._get_session():
            session.add(role)
            try:
                await session.commit()
                return role
            except IntegrityError:
                await session.rollback()
                raise RoleException(message="Role with this name already exists.")

    async def delete_role_by_name(self, role_name: str) -> None:
        async for session in self._get_session():
            role = await session.execute(select(Role).filter(Role.name == role_name))
            role = role.scalars().first()
            if role is None:
                raise RoleException(f"Role with name '{role_name}' does not exist.")
            await session.delete(role)
            await session.commit()

    async def get_roles(self, limit: int = None, offset: int = None) -> list[RoleSchemas]:
        async for session in self._get_session():
            query = select(Role)
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_role_by_name(self, role_name: str) -> Role:
        async for session in self._get_session():
            role_db = await session.execute(select(Role).where(Role.name == role_name))
            role_db = role_db.scalar()
            if role_db is None:
                raise RoleException(f"The role {role_name} does not exist.")
            return role_db

    async def update_role(self, role: RoleSchemas) -> Role:
        async for session in self._get_session():
            role_db = await session.execute(
                select(Role).where(Role.name == role.name)
            )
            role_db = role_db.scalar_one_or_none()
            if role_db is None:
                raise RoleException(f"The role with the name {role.name} was not found in the database.")
            role_db.description = role.description
            session.add(role_db)
            await session.commit()
            return role_db

    async def get_user_by_login(self, login: str) -> User | None:
        async for session in self._get_session():
            query = select(User).where(User.login == login)
            result = await session.execute(query)
            return result.scalars().first()

    async def assign_role_to_user(self, user: User, role: Role) -> None:
        async for session in self._get_session():
            user_role = UserRole(user_id=user.id, role_id=role.id)
            session.add(user_role)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise RoleException("This role is already assigned to this user.")

    async def remove_role_from_user(self, user: User, role: Role) -> None:
        async for session in self._get_session():
            user_role = await session.execute(
                select(UserRole).where(and_(UserRole.user_id == user.id, UserRole.role_id == role.id))
            )
            user_role = user_role.scalars().first()
            if user_role is None:
                raise RoleException("This role is not assigned to this user.")
            await session.delete(user_role)
            await session.commit()
