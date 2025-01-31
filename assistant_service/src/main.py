from contextlib import asynccontextmanager

import uvicorn
from api.v1 import chat, healthy
from core.config import settings
from core.logger import get_logger
from database.mongodb import AsyncMongoClient
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from llm import LLMClient

from text_vector_service import TextVectorClient

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Service started")
    app.state.mongo = AsyncMongoClient(settings.MONGO.uri)
    app.state.llm = LLMClient(address=settings.LLM.address)
    app.state.text_vector = TextVectorClient(address=settings.TEXT_VECTOR.address)

    # Shutdown
    try:
        yield
    finally:

        await app.state.mongo.close()
        logger.info("Service stopped")


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.include_router(chat.router, prefix='/api/v1/assistant', tags=['AI assistant'])
app.include_router(healthy.router, prefix='/api/v1/healthy', tags=['Health Check'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.HOST,
        port=settings.PORT,
    )
