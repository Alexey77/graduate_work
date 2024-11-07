import asyncio
import signal
import sys
import warnings
from pathlib import Path

import grpc
from src.core.config import grpc_server_settings as settings
from src.core.logger import get_logger
from src.grpc_generated import llm_pb2_grpc
from src.handlers import LLMHandler

warnings.filterwarnings("ignore", category=UserWarning)

current_dir = Path(__file__).parent.resolve()
grpc_generated_path = current_dir / 'grpc_generated'
sys.path.insert(0, str(grpc_generated_path))

# ruff: noqa: E402


logger = get_logger(__name__)


async def stop_server(server):
    await server.stop(settings.TIMEOUT)
    logger.info("Server stopped successfully.")


async def serve():
    server = grpc.aio.server()
    handler = LLMHandler()

    llm_pb2_grpc.add_LlmServiceServicer_to_server(handler, server)
    server.add_insecure_port(f'{settings.HOST}:{settings.PORT}')
    logger.info(f"The server is running on host: {settings.HOST}, port:{settings.PORT}")

    await server.start()

    def graceful_shutdown():
        logger.info("Shutting down gracefully...")
        asyncio.create_task(stop_server(server))

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, graceful_shutdown)

    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
