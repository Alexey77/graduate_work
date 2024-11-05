from abc import ABC, abstractmethod


class IAsyncJWTManager(ABC):
    @abstractmethod
    async def create_access_token(
        self, subject: str, role: dict[str, list[str]], **kwargs
    ) -> str: ...

    @abstractmethod
    async def create_refresh_token(
        self, subject: str, role: dict[str, list[str]], **kwargs
    ) -> str: ...

    @abstractmethod
    async def create_tokens(
        self, subject: str, role: dict, **kwargs
    ) -> tuple[str, str]: ...

    @abstractmethod
    async def validate_access_token(self, access_token: str, **kwargs) -> bool: ...

    @abstractmethod
    async def refresh_tokens(
        self, refresh_token: str, role: dict[str, list[str]], **kwargs
    ) -> tuple[str, str]: ...

    @abstractmethod
    async def get_login_from_access_token(self, token: str) -> str: ...

    @abstractmethod
    async def get_roles_from_token(self, token: str) -> list[str]: ...
