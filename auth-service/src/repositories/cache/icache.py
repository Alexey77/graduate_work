from abc import ABC, abstractmethod


class IAsyncCache(ABC):

    @property
    @abstractmethod
    def client(self): ...

    @abstractmethod
    async def delete(self, key: str) -> bool: ...

    @abstractmethod
    async def get(self, key: str) -> str | None: ...

    @abstractmethod
    async def set(self, key: str, value: str, **kwargs) -> bool: ...

    @abstractmethod
    async def close(self, *args, **kwargs) -> None: ...
