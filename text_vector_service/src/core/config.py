from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GRPCServerSettings(BaseSettings):
    HOST: Annotated[str, Field(min_length=1)]
    PORT: Annotated[int, Field(gt=1023, lt=65536)]
    TIMEOUT: Annotated[int, Field(gt=0)]

    model_config = SettingsConfigDict(
        env_prefix='GPRCSERVER_',
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8')


class EncoderSettings(BaseSettings):
    LOCAL_MODEL_PATH: Annotated[str, Field(min_length=1)]
    DEFAULT_MODEL_NAME: Annotated[str, Field(min_length=1)]

    ALLOWED_MODELS: set[str] = {
        "paraphrase-multilingual-mpnet-base-v2",
        "distiluse-base-multilingual-cased-v2",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "intfloat/multilingual-e5-large",
    }

    model_config = SettingsConfigDict(
        env_prefix='ENCODER_',
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8')


grpc_server_settings = GRPCServerSettings()
encoder_settings = EncoderSettings()
