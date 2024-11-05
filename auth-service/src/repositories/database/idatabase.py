from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from models.entity import Permission, ProviderAccount, User
from models.entity import Role as RoleDB
from schemas import ResponseUserHistory, Role


class IAsyncDatabaseConnection(ABC):
    @abstractmethod
    async def get_engine(self): ...

    @abstractmethod
    async def close(self) -> None: ...


class IAsyncUserDatabase(ABC):
    @abstractmethod
    def __init__(self, db: IAsyncDatabaseConnection): ...

    @abstractmethod
    async def authenticate_user(self, login: str, password: str) -> User | None: ...

    @abstractmethod
    async def get_user_by_login(self, login: str) -> User | None: ...

    @abstractmethod
    async def get_user_by_refresh_token(self, refresh_token: str) -> User | None: ...

    @abstractmethod
    async def get_user_with_provider_accounts(
        self, login: str
    ) -> tuple[User | None, list[ProviderAccount]]: ...

    @abstractmethod
    async def get_user_roles_by_id(self, user_id: UUID) -> Sequence[Role]: ...

    @abstractmethod
    async def update_user_by_login(self, login: str, **kwargs) -> None: ...

    @abstractmethod
    async def create_user(self, user: User, role: Role) -> User: ...

    @abstractmethod
    async def get_user_permissions(self, login: str) -> Sequence[Permission]: ...


class IAsyncRoleDatabase(ABC):
    @abstractmethod
    def __init__(self, db: IAsyncDatabaseConnection): ...

    @abstractmethod
    async def create_role(self, role: Role) -> Role: ...

    @abstractmethod
    async def delete_role_by_name(self, role_name: str) -> None: ...

    @abstractmethod
    async def get_roles(self, limit, offset): ...

    @abstractmethod
    async def get_role_by_name(self, role_name: str) -> RoleDB: ...

    @abstractmethod
    async def update_role(self, role: Role) -> Role: ...

    @abstractmethod
    async def get_user_by_login(self, login: str) -> User | None: ...

    @abstractmethod
    async def assign_role_to_user(self, user: User, role: Role) -> None: ...

    @abstractmethod
    async def remove_role_from_user(self, user: User, role: Role) -> None: ...


class IAsyncSessionDatabase(ABC):
    @abstractmethod
    def __init__(self, db: IAsyncDatabaseConnection): ...

    @abstractmethod
    async def add_user_session(
        self, user_id: UUID, refresh_token: str, **kwargs
    ) -> bool: ...

    @abstractmethod
    async def delete_session(self, refresh_token: str) -> None: ...

    @abstractmethod
    async def delete_all_sessions_by_user_id(self, user_id: UUID) -> int: ...

    @abstractmethod
    async def get_user_sessions_by_user_id(
        self, user_id: UUID
    ) -> ResponseUserHistory: ...


class IProviderDatabase(ABC):
    @abstractmethod
    def __init__(self, db: IAsyncDatabaseConnection): ...

    @abstractmethod
    async def add_provider_account(
        self, provider_account: ProviderAccount
    ) -> ProviderAccount: ...

    @abstractmethod
    async def get_provider_account_by_login(
        self, login: str, provider_name: str
    ) -> ProviderAccount | None: ...
