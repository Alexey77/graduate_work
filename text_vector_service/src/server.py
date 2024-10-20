import signal
import sys
import warnings
from concurrent import futures
from pathlib import Path

import grpc
from core.logger import get_logger
from core.settings import encoder_settings
from core.settings import grpc_server_settings as settings
from model_manager import ModelManager

warnings.filterwarnings("ignore", category=UserWarning)

current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir / 'grpc_generated'))

# ruff: noqa: E402
from grpc_generated import encoder_pb2_grpc
from service.encoder import EncoderServicer

logger = get_logger(__name__)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS))
    encode_servicer = EncoderServicer(manager_model=ModelManager(settings=encoder_settings))
    encoder_pb2_grpc.add_EncoderServiceServicer_to_server(encode_servicer, server)

    server.add_insecure_port(f'{settings.HOST}:{settings.PORT}')
    logger.info(f"The server is running on host: {settings.HOST}, port:{settings.PORT}")

    server.start()

    def graceful_shutdown(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        all_rpcs_done_event = server.stop(settings.TIMEOUT)
        all_rpcs_done_event.wait(timeout=settings.TIMEOUT)
        logger.info("Server successfully stopped")

    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server stopped by KeyboardInterrupt")


if __name__ == '__main__':
    serve()
