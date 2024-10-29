import json
from functools import lru_cache
from typing import TYPE_CHECKING

from dependencies import get_llm_client
from fastapi import Depends
from schemes import ReplyResponseModel, Role

if TYPE_CHECKING:
    from llm_service import LLMClient


class RAGService:
    def __init__(self, llm) -> None:
        self._llm: LLMClient = llm

    async def get_answer(self, messages: dict) -> ReplyResponseModel:
        # system_prompt = "Answer in Russian like Mickey Mouse"
        # system_prompt = "Answer in Russian like Master Yoda"
        system_prompt = "Answer in Russian like Eric Cartman from South Park"

        response = await self._llm.get_completion(service=3,
                                                  model="gpt-4o-mini",
                                                  system=system_prompt,
                                                  max_tokens=150,
                                                  messages=json.dumps([messages], ensure_ascii=False)
                                                  )

        return ReplyResponseModel(messages=[
            messages,
            {"role": Role.assistant.value, "content": response.reply}
        ])


@lru_cache
def get_rag_service(
        llm=Depends(get_llm_client)
) -> RAGService:
    return RAGService(llm)
