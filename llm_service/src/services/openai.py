from typing import Any

from core.logger import get_logger
from networking.aiohttp import send_post

from services.base_service import BaseLLMService

logger = get_logger(__name__)


class OpenAIService(BaseLLMService):

    def __init__(self, api_key: str, base_url: str):
        self._api_key = api_key
        self._base_url = base_url
        logger.info(f"Initialized ProxyAPIService with base_url:{self._base_url}")
        logger.info(f"_api_key:{self._api_key}")

    def prepare_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }
        logger.debug(f"Prepared headers: {headers}")
        return headers

    def prepare_messages(self, system_prompt: str, dialogue: list[dict]) -> list[dict]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            logger.debug("Added system prompt to messages")
        messages.extend(dialogue)
        logger.debug(f"Prepared messages: {messages}")
        return messages

    def prepare_data(self, model_name: str, system_prompt: str, max_tokens: int, dialogue: list[dict]) -> dict:
        data = {
            "model": model_name,
            "messages": self.prepare_messages(system_prompt, dialogue),
            "max_tokens": max_tokens
        }
        logger.info(f"Prepared data with model: {model_name}, max_tokens: {max_tokens}")
        return data

    async def send_post(self, data: dict, headers: dict, proxy=None) -> tuple[int, Any]:
        logger.debug(f"Sending POST request to {self._base_url} with data: {data} and headers: {headers}")
        logger.info(f"Sending POST request to {self._base_url}")
        return await send_post(self._base_url, data, headers)

    def get_reply(self, response: dict[str, Any]) -> str:
        """Extracts and returns the assistant's reply content from the response."""
        try:
            content = response["choices"][0]["message"]["content"]
            logger.debug(f"Extracted content from response: {content}")
            return content
        except (KeyError, IndexError) as e:
            msg = f"Failed to parse response: {response} with error: {e}"
            logger.error(msg)
            raise ValueError
