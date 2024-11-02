from abc import ABC, abstractmethod

from models.user_provider import UserProvider
from starlette.requests import Request


class IProviderService(ABC):

    @abstractmethod
    def get_authorization_url(self, provider_name: str) -> str: ...

    @abstractmethod
    async def authorize(self, provider_name: str, request: Request) -> UserProvider: ...
