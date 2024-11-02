import base64
from abc import ABC, abstractmethod
from typing import Any

from core.provider import ProviderSettings


class IOAuthProvider(ABC):

    def __init__(self, settings: ProviderSettings):
        self._settings = settings

    @abstractmethod
    def get_authorization_url(self) -> str: ...

    @abstractmethod
    async def get_access_token(self, query_params: dict) -> str: ...

    @abstractmethod
    async def get_user_info(self, access_token: str) -> dict[str, Any]: ...

    @staticmethod
    def encode_base64(string: str) -> str:
        return base64.b64encode(string.encode('utf-8')).decode('utf-8')

    @staticmethod
    def decode_base64(base64_string: str) -> str:
        return base64.b64decode(base64_string.encode('utf-8')).decode('utf-8')
