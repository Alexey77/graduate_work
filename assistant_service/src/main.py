from contextlib import asynccontextmanager

import uvicorn
from api.v1 import healthy, rag
from core.config import settings
from core.logger import get_logger
from database.mongodb import AsyncMongoClient
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from llm_service import LLMClient

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Service started")
    app.state.mongo = AsyncMongoClient(settings.MONGO.uri)
    app.state.llm_service = LLMClient(address="localhost:50051")

    # Shutdown
    try:
        yield
    finally:

        # app.state.db.close()
        await app.state.mongo.close()
        await app.state.llm_service.disconnect()
        logger.info("Service stopped")


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)



app.include_router(rag.router, prefix='/api/v1/question', tags=['RAG'])
# app.include_router(assistant.router, prefix='/api/v1/assistant', tags=['Assistant'])
app.include_router(healthy.router, prefix='/api/v1/healthy', tags=['Health Check'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.HOST,
        port=settings.PORT,
    )
