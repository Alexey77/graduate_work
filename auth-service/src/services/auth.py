from functools import lru_cache
from typing import TYPE_CHECKING
from uuid import UUID

from core.config import UserRole
from core.logger import get_logger
from dependencies import get_cache, get_db_connection, get_jwt_manager
from fastapi import Depends
from jwt_manager import IAsyncJWTManager
from jwt_manager.exception import JWTException
from models.entity import ProviderAccount, Role, User
from models.user_provider import UserProvider
from repositories.cache.icache import IAsyncCache
from repositories.database.exception import DBException
from repositories.database.idatabase import (
    IAsyncDatabaseConnection,
    IAsyncSessionDatabase,
)
from repositories.database.provider import ProviderDatabase
from repositories.database.role import RoleDatabase
from repositories.database.session import SessionDatabase
from repositories.database.user import UserDatabase
from schemas import (
    ResponseAuthTokens,
    ResponseUserHistory,
    ResponseUserPermissions,
    UserCredentials,
    UserPassUpdate,
    UserRegistration,
)
from services.exception import AuthException
from services.interface.iauth import IAsyncAuthService

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = get_logger(__name__)


class AuthService(IAsyncAuthService):
    def __init__(
        self,
        cache: IAsyncCache,
        db: IAsyncDatabaseConnection,
        jwt: IAsyncJWTManager,
    ):
        self._cache = cache
        self._jwt = jwt
        self._db_session: IAsyncSessionDatabase = SessionDatabase(db=db)
        self._db_user = UserDatabase(db=db)
        self._db_role = RoleDatabase(db=db)
        self._db_provider = ProviderDatabase(db=db)

    async def user_history(self, access_token: str) -> ResponseUserHistory:
        if not await self.validate_access_token(access_token=access_token):
            raise AuthException(message="The token is invalid")

        try:
            login = await self._jwt.get_login_from_access_token(access_token)
        except JWTException as e:
            raise AuthException(message=e.message)

        if login is None:
            raise AuthException(message="The token is invalid")

        user = await self._db_user.get_user_by_login(login=login)

        return await self._db_session.get_user_sessions_by_user_id(user_id=user.id)

    async def create_tokens(self, user: User, role: dict) -> tuple[str, str]:
        return await self._jwt.create_tokens(subject=user.login, role=role)

    async def add_db_user_session(
        self, user_id: UUID, refresh_token: str, user_agent: str
    ) -> None:
        await self._db_session.add_user_session(
            user_id=user_id, refresh_token=refresh_token, user_agent=user_agent
        )

    async def password_change(self, user: UserPassUpdate, **kwargs) -> None:
        user_db = await self._db_user.authenticate_user(
            login=user.login, password=user.old_password
        )
        if user_db is None:
            raise AuthException(message="The login or password is incorrect.")

        await self._db_user.update_user_by_login(
            login=user_db.login, password=user.new_password
        )

    async def register(self, user: UserRegistration, user_agent: str, **kwargs) -> User:
        logger.info(f"Register new user:{user.login}")
        user = User(**user.dict())

        if await self._db_user.get_user_by_login(user.login):
            raise AuthException(message="User duplication is not allowed")

        role: Role = await self._db_role.get_role_by_name(role_name=UserRole.USER)
        # Цель узнать id роли, чтобы позже использовать
        if role is None:
            # Защита, если база проинициализирована не правильно и в ней нет ролей
            raise AuthException(
                message="The role does not exist! The database is not initialized correctly!"
            )

        logger.info(f"Creating new user:{user.login}")
        try:
            return await self._db_user.create_user(user=user, role=role)
        except DBException as e:
            raise AuthException(message=e.message)

    async def login(
        self, user: UserCredentials, user_agent: str, **kwargs
    ) -> ResponseAuthTokens:
        logger.info(f"Login user:{user.login}")

        user_db = await self._db_user.authenticate_user(
            login=user.login, password=user.password
        )
        if user_db is None:
            raise AuthException(message="The login or password is incorrect.")

        return await self._login_existing_user(user=user_db, user_agent=user_agent)

    async def _login_existing_user(
        self, user: User, user_agent: str
    ) -> ResponseAuthTokens:
        roles: Sequence[Role] = await self._db_user.get_user_roles_by_id(
            user_id=user.id
        )

        _access_token, _refresh_token = await self._jwt.create_tokens(
            subject=user.login, role={"role": [r.name for r in roles]}
        )
        await self._db_session.add_user_session(
            user_id=user.id, refresh_token=_refresh_token, user_agent=user_agent
        )
        return ResponseAuthTokens(
            access_token=_access_token, refresh_token=_refresh_token
        )

    async def _authorize_provider_new_user(
        self, user: UserProvider, user_agent: str, **kwargs
    ):
        user_db = await self.register(
            user=UserRegistration(email=user.login, password=user.password),
            user_agent=user_agent,
        )
        logger.info(
            f"Register new user:{user.login} with provider:{user.provider.value}"
        )
        await self._db_provider.add_provider_account(
            provider_account=ProviderAccount(
                user_id=user_db.id,
                id_social=user.id_social,
                provider_name=user.provider,
            )
        )

        return await self.login(
            UserCredentials(email=user.login, password=user.password),
            user_agent=user_agent,
        )

    async def authorize_provider(
        self, user: UserProvider, user_agent: str, **kwargs
    ) -> ResponseAuthTokens:
        logger.info(f"Login user:{user.login}")

        user_db = await self._db_user.get_user_by_login(login=user.login)
        if user_db is None:
            return await self._authorize_provider_new_user(
                user=user, user_agent=user_agent
            )

        provider_account = await self._db_provider.get_provider_account_by_login(
            login=user.login, provider_name=user.provider
        )
        if provider_account is None:
            await self._db_provider.add_provider_account(
                provider_account=ProviderAccount(
                    user_id=user_db.id,
                    id_social=user.id_social,
                    provider_name=user.provider,
                )
            )

        return await self._login_existing_user(user=user_db, user_agent=user_agent)

    async def refresh_tokens(
        self, refresh_token: str, user_agent: str, **kwargs
    ) -> ResponseAuthTokens:
        user_db = await self._db_user.get_user_by_refresh_token(
            refresh_token=refresh_token
        )
        if user_db is None:
            raise AuthException(message="User is not exists")
        logger.info(f"Refresh token user:{user_db.login}")

        await self._db_session.delete_session(refresh_token=refresh_token)

        roles: Sequence[Role] = await self._db_user.get_user_roles_by_id(
            user_id=user_db.id
        )
        role = {"role": [r.name for r in roles]}

        _access_token, _refresh_token = await self.create_tokens(
            user=user_db, role=role
        )
        await self.add_db_user_session(
            user_id=user_db.id, refresh_token=_refresh_token, user_agent=user_agent
        )

        return ResponseAuthTokens(
            access_token=_access_token, refresh_token=_refresh_token
        )

    async def is_token_revoked(self, access_token: str) -> bool:
        token_status = await self._cache.get(access_token)
        return token_status == "invalid"

    async def push_revoked_jwt(self, access_token: str) -> None:
        await self._cache.set(access_token, "invalid")

    async def logout(self, access_token: str) -> None:
        if await self.is_token_revoked(access_token=access_token):
            raise AuthException(
                message="Your current session has been terminated. Please log in again to continue."
            )
        await self.push_revoked_jwt(access_token=access_token)

    async def logout_from_all_devices(self, access_token: str) -> None:
        if await self.is_token_revoked(access_token=access_token):
            raise AuthException(
                message="Your current session has been terminated. Please log in again to continue."
            )

        await self.push_revoked_jwt(access_token=access_token)

        try:
            login = await self._jwt.get_login_from_access_token(access_token)
        except JWTException as e:
            raise AuthException(message=e.message)

        user = await self._db_user.get_user_by_login(login=login)

        if user is None:
            raise AuthException(
                message="Invalid or expired refresh token or no active sessions"
            )
        count = await self._db_session.delete_all_sessions_by_user_id(user_id=user.id)
        logger.info(f"Deleted {count} sessions for user with login '{user.login}'.")

    async def validate_access_token(self, access_token: str, **kwargs) -> bool:
        if await self.is_token_revoked(access_token=access_token):
            raise AuthException(
                message="Your current session has been terminated. Please log in again to continue."
            )
        try:
            return await self._jwt.validate_access_token(access_token=access_token)
        except JWTException as e:
            raise AuthException(message=e.message)

    async def user_permissions(self, access_token: str) -> ResponseUserPermissions:
        if not await self.validate_access_token(access_token=access_token):
            raise AuthException(message="The token is invalid")

        try:
            login = await self._jwt.get_login_from_access_token(access_token)
        except JWTException as e:
            raise AuthException(message=e.message)

        if login is None:
            raise AuthException(message="The token is invalid")

        permissions = await self._db_user.get_user_permissions(login=login)
        return ResponseUserPermissions(permissions=permissions, login=login)


@lru_cache
def get_auth_service(
    cache: IAsyncCache = Depends(get_cache),
    db: IAsyncDatabaseConnection = Depends(get_db_connection),
    jwt: IAsyncJWTManager = Depends(get_jwt_manager),
) -> AuthService:
    return AuthService(cache, db, jwt)
