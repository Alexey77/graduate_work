from abc import ABC, abstractmethod


class IAsyncAccessService(ABC):
    @abstractmethod
    async def verify_admin_access(self, access_token: str) -> None:
        pass
