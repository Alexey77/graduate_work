from src.core.config import settings
from src.core.logger import get_logger

from .base_service import BaseLLMService
from .openai import OpenAIService

logger = get_logger(__name__)


def get_llm_service(service_name: str) -> BaseLLMService:
    logger.info(f"Attempting to create service for: {service_name}")

    match service_name:
        case "OPENAI":
            service = OpenAIService(api_key=settings.OPENAI.TOKEN,
                                    base_url=settings.OPENAI.BASE_URL)
        case "PROXYAPI":
            service = OpenAIService(api_key=settings.PROXYAPI.TOKEN,
                                    base_url=settings.PROXYAPI.BASE_URL)
        case _:
            logger.error(f"Service {service_name} not supported")
            msg = f"Service {service_name} not supported"
            raise NotImplementedError(msg)

    logger.info(f"Service {service_name} created successfully")
    return service
