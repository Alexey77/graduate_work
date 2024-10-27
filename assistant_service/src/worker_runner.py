import asyncio

from core.config import settings
from queues.rabbitmq_connection import RabbitMQConnection


async def main():
    connection = RabbitMQConnection(settings=settings.RABBIT)



if __name__ == "__main__":
    asyncio.run(main())
