import asyncio
import signal
import sys
import warnings
from pathlib import Path

import grpc
from core.config import grpc_server_settings as settings
from core.logger import get_logger
from handlers import LLMHandler

warnings.filterwarnings("ignore", category=UserWarning)

current_dir = Path(__file__).parent.resolve()
grpc_generated_path = current_dir / 'grpc_generated'
sys.path.insert(0, str(grpc_generated_path))

# ruff: noqa: E402
from grpc_generated import llm_pb2_grpc

logger = get_logger(__name__)


async def serve():
    server = grpc.aio.server()
    handler = LLMHandler()

    llm_pb2_grpc.add_LlmServiceServicer_to_server(handler, server)

    server.add_insecure_port(f'{settings.HOST}:{settings.PORT}')
    logger.info(f"The server is running on host: {settings.HOST}, port:{settings.PORT}")

    await server.start()

    def graceful_shutdown(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        asyncio.create_task(server.stop(settings.TIMEOUT))
        logger.info("Server successfully stopped")

    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    await server.wait_for_termination()


if __name__ == '__main__':
    # serve()
    asyncio.run(serve())
