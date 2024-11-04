import asyncio
import signal
import sys
import warnings
from pathlib import Path
import grpc
from core.config import encoder_settings, vector_db_settings
from core.config import grpc_server_settings as settings
from core.logger import get_logger
from model_manager import ModelManager
import grpc_reflection.v1alpha.reflection as reflection
warnings.filterwarnings("ignore", category=UserWarning)

current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir / 'grpc_generated'))
sys.path.insert(0, str(current_dir / 'handlers'))
# ruff: noqa: E402
from grpc_generated import encoder_pb2_grpc, similarity_search_pb2_grpc, encoder_pb2, similarity_search_pb2
from handlers.encoder import EncoderServicer
from handlers.similarity_search import SimilaritySearchServicer

logger = get_logger(__name__)

async def stop_server(server, db_connection, manager_model):
    await server.stop(settings.TIMEOUT)
    logger.info("Server stopped successfully.")

    # Освобождаем ресурсы модели
    manager_model.unload_models()
    logger.info("Models unloaded successfully.")

    # Закрываем соединение с базой данных
    db_connection = False  # noqa F841
    logger.info("Database connection closed successfully.")


async def serve():
    server = grpc.aio.server()

    # Создаем экземпляр ModelManager
    manager_model = ModelManager(settings=encoder_settings)

    encode_servicer = EncoderServicer(manager_model=manager_model)
    similarity_search_servicer = SimilaritySearchServicer(settings=vector_db_settings,
                                                          manager_model=manager_model)

    encoder_pb2_grpc.add_EncoderServiceServicer_to_server(encode_servicer, server)
    similarity_search_pb2_grpc.add_SimilaritySearchServiceServicer_to_server(similarity_search_servicer, server)

    SERVICE_NAMES = (
        encoder_pb2.DESCRIPTOR.services_by_name['EncoderService'].full_name,
        similarity_search_pb2.DESCRIPTOR.services_by_name['SimilaritySearchService'].full_name,
        reflection.SERVICE_NAME,
    )

    # Register the reflection service
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port(f'{settings.HOST}:{settings.PORT}')
    logger.info(f"The server is running on host: {settings.HOST}, port:{settings.PORT}")

    db_connection = True

    await server.start()

    def graceful_shutdown():
        logger.info("Shutting down gracefully...")
        # Запускаем stop_server как задачу, не блокируя основной поток
        asyncio.create_task(stop_server(server, db_connection, manager_model))

    # Регистрируем обработчики сигналов для корректного завершения
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, graceful_shutdown)

    # Ожидаем завершения сервера
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
