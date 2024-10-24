import aio_pika

from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel

from core.config import RabbitMQSettings

from .base_connection import IAsyncQueueConnection


class RabbitMQConnection(IAsyncQueueConnection):
    _connection: AbstractRobustConnection | None = None
    _channel: AbstractRobustChannel | None = None

    def __init__(self, settings: RabbitMQSettings) -> None:
        self._settings = settings

    async def get_connection(self) -> AbstractRobustConnection:
        if self._connection is None:
            self._connection = await aio_pika.connect_robust(self._settings.uri)
        return self._connection

    async def get_channel(self) -> AbstractRobustChannel:
        if self._channel is None:
            if self._connection is None:
                await self.get_connection()
            self._channel = await self._connection.channel()
        return self._channel

    async def close(self) -> None:
        if self._channel:
            await self._channel.close()
            self._channel = None
        if self._connection:
            await self._connection.close()
            self._connection = None
