from functools import lru_cache

from core.config import UserRole
from core.logger import get_logger
from dependencies import get_access_service, get_role_db
from fastapi import Depends
from models.entity import Role as RoleDB
from models.entity import User
from repositories.database.idatabase import IAsyncRoleDatabase
from schemas import Role
from services.exception import AccessException, RoleException
from services.interface.iaccess import IAsyncAccessService
from services.interface.iroles import IAsyncRoles

logger = get_logger(__name__)


class RolesService(IAsyncRoles):
    def __init__(self, db: IAsyncRoleDatabase, access_service: IAsyncAccessService):
        self._db = db
        self._access_service = access_service

    async def create_role(self, role: Role, access_token: str):
        try:
            await self._access_service.verify_admin_access(access_token=access_token)
        except AccessException as e:
            raise RoleException(message=e.message)
        return await self._db.create_role(role=role)

    async def get_roles(
        self, limit: int | None = None, offset: int | None = None
    ) -> list[Role]:
        return await self._db.get_roles(limit=limit, offset=offset)

    async def delete_role_by_name(self, role_name: str, access_token: str) -> None:
        try:
            await self._access_service.verify_admin_access(access_token=access_token)
        except AccessException as e:
            raise RoleException(message=e.message)

        if role_name in UserRole.__members__.values():
            msg = "Modifications for specified roles are restricted via API. Please contact an administrator."
            raise AccessException(message=msg)
        return await self._db.delete_role_by_name(role_name=role_name)

    async def update_role(self, role: Role, access_token: str):
        try:
            await self._access_service.verify_admin_access(access_token=access_token)
        except AccessException as e:
            raise RoleException(message=e.message)
        return await self._db.update_role(role=role)

    async def get_role_by_name(self, role_name: str) -> Role:
        role_db: RoleDB = await self._db.get_role_by_name(role_name=role_name)
        return Role(name=role_db.name, description=role_db.description)

    async def _handle_role_assignment(
        self, user_name: str, role_name: str, access_token: str
    ) -> tuple[RoleDB, User]:
        try:
            await self._access_service.verify_admin_access(access_token=access_token)
        except AccessException as e:
            raise RoleException(message=e.message)

        role_db: RoleDB = await self._db.get_role_by_name(role_name=role_name)
        user_db = await self._db.get_user_by_login(login=user_name)

        if role_db is None or user_db is None:
            msg = "The role name or user name is incorrect"
            raise RoleException(message=msg)
        return role_db, user_db

    async def assign_role_to_user(
        self, user_name: str, role_name: str, access_token: str
    ) -> None:
        role_db, user_db = await self._handle_role_assignment(
            user_name=user_name, role_name=role_name, access_token=access_token
        )
        await self._db.assign_role_to_user(user=user_db, role=role_db)

    async def revoke_role_from_user(
        self, user_name: str, role_name: str, access_token: str
    ) -> None:
        role_db, user_db = await self._handle_role_assignment(
            user_name=user_name, role_name=role_name, access_token=access_token
        )
        await self._db.remove_role_from_user(user=user_db, role=role_db)


@lru_cache
def get_role_service(
    db: IAsyncRoleDatabase = Depends(get_role_db),
    access_service: IAsyncAccessService = Depends(get_access_service),
) -> IAsyncRoles:
    return RolesService(db, access_service)
