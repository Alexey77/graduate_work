from abc import ABC, abstractmethod

from schemas import Role


class IAsyncRoles(ABC):

    @abstractmethod
    async def create_role(self, role: Role, access_token: str): ...

    @abstractmethod
    async def delete_role_by_name(self, role_name: str, access_token: str) -> None: ...

    @abstractmethod
    async def get_roles(self, limit: int | None = None, offset: int | None = None) -> list[Role]: ...

    @abstractmethod
    async def get_role_by_name(self, role_name: str) -> Role: ...

    @abstractmethod
    async def update_role(self, role: Role, access_token: str) -> Role: ...

    @abstractmethod
    async def assign_role_to_user(self, user_name: str, role_name: str, access_token: str) -> None: ...

    @abstractmethod
    async def revoke_role_from_user(self, user_name: str, role_name: str, access_token: str) -> None: ...
