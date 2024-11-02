from abc import ABC, abstractmethod

from models.user_provider import UserProvider
from schemas import (ResponseAuthTokens, ResponseUserHistory,
                     ResponseUserPermissions, UserCredentials, UserPassUpdate,
                     UserRegistration)


class IAsyncAuthService(ABC):
    @abstractmethod
    async def register(self, user: UserRegistration, user_agent: str, **kwargs) -> None: ...

    @abstractmethod
    async def login(self, user: UserCredentials, user_agent: str, **kwargs) -> ResponseAuthTokens: ...

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str, user_agent: str, **kwargs) -> ResponseAuthTokens: ...

    @abstractmethod
    async def authorize_provider(self, user: UserProvider, user_agent: str, **kwargs) -> ResponseAuthTokens: ...

    @abstractmethod
    async def validate_access_token(self, access_token: str, **kwargs) -> bool: ...

    @abstractmethod
    async def logout_from_all_devices(self, access_token: str) -> None: ...

    @abstractmethod
    async def logout(self, access_token: str) -> None: ...

    @abstractmethod
    async def password_change(self, user: UserPassUpdate, **kwargs) -> None: ...

    @abstractmethod
    async def user_history(self, access_token: str) -> ResponseUserHistory: ...

    @abstractmethod
    async def user_permissions(self, access_token: str) -> ResponseUserPermissions: ...
