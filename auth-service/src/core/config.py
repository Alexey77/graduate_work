from enum import Enum
from logging import config as logging_config
from pathlib import Path

from core.logger import LOGGING
from pydantic import conint, constr
from pydantic_settings import BaseSettings
from repositories.enums import CacheStorageEnum, DBStorageEnum

logging_config.dictConfig(LOGGING)


class UserRole(str, Enum):
    ADMINISTRATOR = "admin"
    GUEST = "guest"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Auth service"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    HOST: constr(min_length=1)
    PORT: conint(gt=1023, lt=65536)

    MAXIMUM_SESSION_PER_USER: conint(gt=0) = 5  # одновременно подключенных устройств одним пользователем
    REQUEST_LIMIT_PER_MINUTE: conint(gt=0) = 20  # лимит запросов в минуту на 1 пользователя

    RATE_LIMIT_TTL: conint(gt=0) = 60  # requests per 1 minute per user

    class Config:
        extra = 'ignore'
        env_file = './auth-service/.env'
        env_file_encoding = 'utf-8'
        env_prefix = 'SERVICE_'


class JWTSettings(BaseSettings):
    authjwt_secret_key: str
    authjwt_access_token_expires: int | None = None
    authjwt_refresh_token_expires: int | None = None

    class Config:
        extra = 'ignore'
        env_file = './auth-service/.env'
        env_file_encoding = 'utf-8'
        env_prefix = 'JWT_'


class TraceSettings(BaseSettings):
    SERVICE_NAME: constr(min_length=1) = 'auth-service'
    USE_TRACE: bool = False
    HOST: constr(min_length=1)
    PORT: conint(gt=1023, lt=65536)

    TO_CONSOLE: bool = True

    class Config:
        extra = 'ignore'
        env_file = './auth-service/.env'
        env_file_encoding = 'utf-8'
        env_prefix = 'JAEGER_'


class CacheSettings(BaseSettings):
    cache_storage: str = CacheStorageEnum.REDIS

    host: constr(min_length=1)
    port: conint(gt=1023, lt=65536)

    expiration_time: int

    class Config:
        extra = 'ignore'
        env_file = './auth-service/.env'
        env_file_encoding = 'utf-8'
        env_prefix = 'REDIS_'


class DBSettings(BaseSettings):
    db_storage: str = DBStorageEnum.POSTGRESQL
    URI: str
    URI_FOR_CLI: str
    URI_FOR_ALEMBIC: str
    SQLALCHEMY_ECHO: bool = False

    class Config:
        extra = 'ignore'
        env_file = './auth-service/.env'
        env_file_encoding = 'utf-8'
        env_prefix = 'DB_'


settings = Settings()
cache_settings = CacheSettings()
db_settings = DBSettings()
trace_settings = TraceSettings()
