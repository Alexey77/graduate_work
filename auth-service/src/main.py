from contextlib import asynccontextmanager

import uvicorn
from api.v1 import auth, healthy, roles
from core.config import (JWTSettings, cache_settings, db_settings, settings,
                         trace_settings)
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from jwt_manager import jwt_manager_factory
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from rate_limiter import get_track_request
from repositories.cache import IAsyncCache, cache_factory
from repositories.database import IAsyncDatabaseConnection, db_factory
from tracers import configure_tracer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.cache: IAsyncCache = cache_factory(settings=cache_settings)
    app.state.db: IAsyncDatabaseConnection = db_factory(settings=db_settings)
    app.state.jwt_manager = jwt_manager_factory(settings=JWTSettings())

    yield
    # shutdown
    await app.state.cache.close()
    await app.state.db.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

if trace_settings.USE_TRACE:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)

app.include_router(auth.router, prefix='/api/v1/auth', tags=['Authorization'])
app.include_router(roles.router, prefix='/api/v1/roles', tags=['Roles'])
app.include_router(healthy.router, prefix='/api/v1/healthy', tags=['Health Check'])


@app.middleware("http")
async def check_request_id(request: Request, call_next):
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                              content={'detail': 'X-Request-Id is required'})
    response = await call_next(request)
    return response


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.headers.get('X-Request-Id') == 'healthcheck':  # docker healthcheck
        return await call_next(request)

    cache_client = app.state.cache.client
    track_request = get_track_request(client=cache_client)

    user_id = request.headers.get('X-Forwarded-For')
    request_number = await track_request(user_id=user_id, client=cache_client)
    if request_number > settings.REQUEST_LIMIT_PER_MINUTE:
        return ORJSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                              content={'detail': 'Too many requests'})

    response = await call_next(request)
    return response


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.HOST,
        port=settings.PORT,
    )
