from enum import Enum

from pydantic import HttpUrl, constr
from pydantic_settings import BaseSettings


class Provider(str, Enum):
    YANDEX = "yandex"
    GOOGLE = "google"


class ProviderSettings(BaseSettings):
    CLIENT_ID: constr(min_length=1)
    CLIENT_SECRET: constr(min_length=1)
    REDIRECT_URL: HttpUrl


class YandexProviderSettings(ProviderSettings):
    class Config:
        extra = "ignore"
        env_file = "./auth-service/.env"
        env_file_encoding = "utf-8"
        env_prefix = "YANDEX_"


class GoogleProviderSettings(ProviderSettings):
    class Config:
        extra = "ignore"
        env_file = "./auth-service/.env"
        env_file_encoding = "utf-8"
        env_prefix = "GOOGLE_"
