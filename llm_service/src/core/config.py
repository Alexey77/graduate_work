from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GRPCServerSettings(BaseSettings):
    HOST: Annotated[str, Field(min_length=1)]
    PORT: Annotated[int, Field(gt=1023, lt=65536)]
    MAX_WORKERS: Annotated[int, Field(gt=0)]
    TIMEOUT: Annotated[int, Field(gt=0)]

    model_config = SettingsConfigDict(
        env_prefix='GPRCSERVER_',
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8')


class ProxySocks5(BaseSettings):
    HOST: str = Field(min_length=1)
    PORT: int = Field(gt=1023, lt=65536)
    LOGIN: str | None = None
    PASSWORD: str | None = None

    def to_proxy_url(self) -> str:
        if self.LOGIN and self.PASSWORD:
            return f"socks5://{self.LOGIN}:{self.PASSWORD}@{self.HOST}:{self.PORT}"
        return f"socks5://{self.HOST}:{self.PORT}"

    model_config = SettingsConfigDict(
        env_prefix='PROXY_',
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8')


class OpenAISettings(BaseSettings):
    TOKEN: Annotated[str, Field(min_length=1)]
    BASE_URL: str

    model_config = SettingsConfigDict(
        env_prefix='OPENAI_',
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8')


class ProxyAPISettings(BaseSettings):
    TOKEN: Annotated[str, Field(min_length=1)]
    BASE_URL: str

    model_config = SettingsConfigDict(
        env_prefix='PROXYAPI_',
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8')


class Settings(BaseSettings):
    OPENAI: OpenAISettings | None = None
    PROXYAPI: ProxyAPISettings | None = None
    PROXY: ProxySocks5 | None = None


settings = Settings(
    OPENAI=OpenAISettings(),
    PROXYAPI=ProxyAPISettings(),
    PROXY=ProxySocks5()
)

grpc_server_settings = GRPCServerSettings()
