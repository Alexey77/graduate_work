from fastapi import Depends, FastAPI
from jwt_manager import IAsyncJWTManager
from repositories.cache import IAsyncCache
from repositories.database.idatabase import (IAsyncDatabaseConnection,
                                             IAsyncRoleDatabase,
                                             IAsyncUserDatabase)
from repositories.database.role import RoleDatabase
from repositories.database.user import UserDatabase
from services.access import AccessService
from services.interface.iaccess import IAsyncAccessService
from services.provider import ProviderService


def get_app() -> FastAPI:
    from main import app
    return app


def get_cache(app: FastAPI = Depends(get_app)) -> IAsyncCache:
    return app.state.cache


def get_db(app: FastAPI = Depends(get_app)) -> IAsyncDatabaseConnection:
    return app.state.db


async def get_auth_db(app: FastAPI = Depends(get_app)) -> IAsyncUserDatabase:
    return UserDatabase(db=app.state.db)


async def get_role_db(app: FastAPI = Depends(get_app)) -> IAsyncRoleDatabase:
    return RoleDatabase(db=app.state.db)


async def get_db_connection(app: FastAPI = Depends(get_app)) -> IAsyncDatabaseConnection:
    return app.state.db


def get_jwt_manager(app: FastAPI = Depends(get_app)) -> IAsyncJWTManager:
    return app.state.jwt_manager


def get_access_service(jwt: IAsyncJWTManager = Depends(get_jwt_manager)) -> IAsyncAccessService:
    return AccessService(jwt=jwt)


def get_provider_service() -> ProviderService:
    return ProviderService()
