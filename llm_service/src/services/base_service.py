from abc import ABC, abstractmethod
from typing import Any

from core.config import ProxySocks5


class BaseLLMService(ABC):
    @abstractmethod
    def prepare_headers(self) -> dict: ...

    @abstractmethod
    def prepare_data(self, model_name: str, system_prompt: str, max_tokens: int, dialogue: list[dict]) -> dict: ...

    @abstractmethod
    async def send_post(self, data: dict, headers: dict, proxy: ProxySocks5 | None = None) -> tuple[int, Any]: ...

    @abstractmethod
    def prepare_messages(self, system_prompt: str, dialogue: list[dict]) -> list[dict]: ...

    @abstractmethod
    def get_reply(self, response: dict[str, Any]) -> list[dict]: ...

    """Extracts and returns the assistant's reply content from the response."""
