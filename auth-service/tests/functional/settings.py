import os

from pydantic import constr
from pydantic_settings import BaseSettings


class ServiceSettings(BaseSettings):
    service_base_api_url: constr(min_length=1)

    class Config:
        extra = 'ignore'
        env_file = os.path.abspath('./tests/functional/.env')
        env_file_encoding = 'utf-8'


class DBSettings(BaseSettings):
    db_uri: constr(min_length=1)
    db_uri_for_tests: constr(min_length=1)

    class Config:
        extra = 'ignore'
        env_file = os.path.abspath('./tests/functional/.env')
        env_file_encoding = 'utf-8'


class CacheSettings(BaseSettings):
    redis_host: constr(min_length=1)
    redis_port: constr(min_length=1)
    redis_ex: constr(min_length=1)

    class Config:
        extra = 'ignore'
        env_file = os.path.abspath('./tests/functional/.env')
        env_file_encoding = 'utf-8'


service_settings = ServiceSettings()
db_setting = DBSettings()
cache_settings = CacheSettings()
