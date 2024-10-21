from pathlib import Path
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: Annotated[str, Field(min_length=1)]
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    HOST: Annotated[str, Field(min_length=1)]
    PORT: Annotated[int, Field(gt=1023, lt=65536)]

    model_config = SettingsConfigDict(
        env_prefix='SERVICE_',
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8')


settings = Settings()
