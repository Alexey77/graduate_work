from abc import ABC, abstractmethod
from typing import Any


class IAsyncQueueConnection(ABC):
    @abstractmethod
    async def get_connection(self) -> Any:
        """
        Возвращает асинхронное подключение к очереди.

        :return: Объект, представляющий подключение к очереди.
        """

    async def get_channel(self) -> Any:
        """
        Возвращает асинхронный канал для работы с очередями.

        :return: Объект, представляющий канал очереди.
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Закрывает соединение с очередью.
        """
