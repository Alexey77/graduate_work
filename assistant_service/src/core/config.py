from pathlib import Path
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthServiceSettings(BaseSettings):
    pass
    # url: Annotated[str, Field(min_length=1)]
    # secret_key: Annotated[str, Field(min_length=1)]
    # algorithm: Annotated[str, Field(default="HS256", min_length=1)]
    #
    # model_config = SettingsConfigDict(
    #     env_prefix='AUTH_SERVICE_',
    #     env_file='.env',
    #     extra='ignore',
    #     env_file_encoding='utf-8'
    # )


class GrpcServiceSettings(BaseSettings):
    HOST: Annotated[str, Field(min_length=1)]
    PORT: Annotated[int, Field(gt=1023, lt=65536)]

    DEFAULT_SERVICE: Annotated[int, Field(gt=0, lt=5)]
    DEFAULT_MODEL: Annotated[str, Field(min_length=1)]

    INTENT_SERVICE: Annotated[int, Field(gt=0, lt=5)]
    INTENT_MODEL: Annotated[str, Field(min_length=1)]

    RAG_SERVICE: Annotated[int, Field(gt=0, lt=5)]
    RAG_MODEL: Annotated[str, Field(min_length=1)]

class IntentSettings(BaseSettings): # TODO вынести из GrpcServiceSettings
    pass

class LLMService(GrpcServiceSettings):

    model_config = SettingsConfigDict(
        env_prefix='LLMSERVICE_',
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8'
    )


class MongoDBSettings(BaseSettings):
    USER: Annotated[str, Field(min_length=0)] = ''
    PASSWORD: Annotated[str, Field(min_length=0)] = ''
    HOST: Annotated[str, Field(min_length=1)]
    PORT: Annotated[int, Field(gt=1023, lt=65536)]
    DB_NAME: Annotated[str, Field(min_length=1)]
    COLLECTION_NAME: Annotated[str, Field(min_length=1)]

    @property
    def uri(self) -> str:
        if self.USER and self.PASSWORD:
            return f'mongodb://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/?authMechanism=DEFAULT'
        return f'mongodb://{self.HOST}:{self.PORT}/{self.DB_NAME}'

    model_config = SettingsConfigDict(
        env_prefix='MONGODB_',
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8'
    )


class Settings(BaseSettings):
    PROJECT_NAME: Annotated[str, Field(min_length=1)]
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    HOST: Annotated[str, Field(min_length=1)]
    PORT: Annotated[int, Field(gt=1023, lt=65536)]

    MONGO: MongoDBSettings = MongoDBSettings()
    LLM: LLMService = LLMService()

    model_config = SettingsConfigDict(
        env_prefix='SERVICE_',
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8')


settings = Settings()
auth_service_settings = AuthServiceSettings()
