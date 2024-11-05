from abc import ABC, abstractmethod


class INetworkClient(ABC):
    @abstractmethod
    async def get(self, url: str, params: dict = None) -> dict: ...

    @abstractmethod
    async def post(self, url: str, data: dict = None) -> dict: ...
