from functools import lru_cache

from fastapi import Depends

from dependencies import get_llm_client
from llm import LLMClient
from schemes import AssistantMessage, UserMessage


class ChatService:
    def __init__(self, llm_client: LLMClient, ):
        self._llm = llm_client

    async def get_answer(self, messages: list[UserMessage | AssistantMessage], user: str):
        pass


@lru_cache
def get_chat_service(
        llm_client=Depends(get_llm_client)
) -> ChatService:
    return ChatService(
        llm_client
    )
