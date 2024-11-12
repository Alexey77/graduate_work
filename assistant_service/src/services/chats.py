import json
from functools import lru_cache

from core.config import settings
from core.logger import get_logger
from dependencies import get_llm_client
from fastapi import Depends
from icecream import ic
from llm import LLMClient
from prompts import get_system_prompt_for_function
from schemes import AssistantMessage, UserMessage
from services.exception import ChatException

logger = get_logger(__name__)


class ChatService:
    def __init__(self, llm_client: LLMClient):
        self._llm = llm_client

    async def get_answer(self, messages: list[UserMessage | AssistantMessage], user: str):

        intent_function: dict = await self._determine_intent([msg.model_dump() for msg in messages])
        ic(intent_function)

        try:
            method = intent_function["name"]
            arguments = json.loads(intent_function["arguments"])
        except KeyError:
            raise ChatException

        answer = await getattr(self, method)(**arguments)

        messages.append(AssistantMessage(role="assistant",
                                         content=answer))

        return messages

    async def _determine_intent(self, messages, **kwargs):

        functions_desc = self.create_list_functions_description()
        try:
            response = await self._llm.get_functions(service=settings.INTENT.SERVICE,
                                                     model=settings.INTENT.MODEL,
                                                     system=get_system_prompt_for_function(),
                                                     max_tokens=kwargs.get("max_tokens", 150),
                                                     messages=json.dumps(messages, ensure_ascii=False),
                                                     functions=json.dumps(functions_desc, ensure_ascii=False),
                                                     function_call=kwargs.get("function_call", "auto")
                                                     )

        except Exception as e:  # noqa BLE001
            logger.error(str(e))
            raise ChatException(e)

        if response.status_code == 200:
            return json.loads(response.reply)

        msg = f"Intent classification failed with status code {response.status_code} and reply: {response.response}"
        logger.error(msg)
        raise ChatException(msg)

    def create_list_functions_description(self) -> list[dict[str, str]]:

        # functions in the definition of intent
        functions = [self.get_information_from_rag,
                     self.handle_unknown_intent]
        result = []

        for func in functions:
            doc = func.__doc__
            if doc is None:
                logger.warning(f"Function {doc} does not contain a description")
                continue

            doc_dict = json.loads(doc)
            doc_dict.pop("name", None)
            doc_dict["name"] = func.__name__

            result.append(doc_dict)

        return result

    async def get_information_from_rag(self, eng: str, rus: str) -> str:
        """
        {
            "description": "Extracts the main intent of the user's query and forms a search query in both Russian and English.",
            "parameters": {
                "type": "object",
                "properties": {
                    "eng": {
                        "type": "string",
                        "description": "Search query in English."
                    },
                    "rus": {
                        "type": "string",
                        "description": "Search query in Russian."
                    }
                },
                "required": ["eng", "rus"]
            }
        }
        """

        return f"RAG rus:{rus}, eng:{eng}"

    async def handle_unknown_intent(self, answer: str) -> str:
        """
        {
        "description": "Handles an unknown or unclear user intent.",
        "parameters": {
            "type": "object",
            "properties": {
                "answer": {
                    "type": "string",
                    "description": "A message indicating that the user's intent was not understood."
                }
            },
            "required": ["answer"]
            }
        }
        """

        return answer


@lru_cache
def get_chat_service(
        llm_client=Depends(get_llm_client)
) -> ChatService:
    return ChatService(
        llm_client
    )
