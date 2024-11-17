import json
from functools import lru_cache

from core.config import settings
from core.logger import get_logger
from dependencies import get_llm_client, get_text_vector_client
from fastapi import Depends
from grpc.aio import AioRpcError
from llm import LLMClient
from prompts import get_system_prompt_for_function, get_system_prompt_for_rag
from schemes import AssistantMessage, SystemMessage, UserMessage
from services.exception import ChatException

from text_vector_service import TextVectorClient

logger = get_logger(__name__)


class ChatService:
    def __init__(self, llm_client: LLMClient, text_vector_client: TextVectorClient):
        self._llm = llm_client
        self._text_vector = text_vector_client

    async def get_answer(self, messages: list[UserMessage | AssistantMessage], user: str):

        intent_function: dict = await self._determine_intent([msg.model_dump() for msg in messages])

        # Пример intent_function на запрос - "какой актер играл Ломоносова"
        # intent_function = {"arguments": '{"eng": "Which actor played Lomonosov?", "rus": "Какой актер играл Ломоносова?"}',
        #                    "name": "get_information_from_rag"}

        try:
            method = intent_function["name"]
            arguments = json.loads(intent_function["arguments"])
        except KeyError:
            raise ChatException

        messages = await getattr(self, method)(messages, **arguments)

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

        except AioRpcError as e:
            logger.error(str(e))
            raise ChatException(e)
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

    async def get_information_from_rag(self, messages: list, eng: str, rus: str) -> list:
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

        enrich_data = await self._enrich_data_for_rag(text_query=rus)

        system_prompt = get_system_prompt_for_rag(enrich_data)

        try:
            response = await self._llm.get_completion(service=settings.RAG.SERVICE,
                                                      model=settings.RAG.MODEL,
                                                      system=system_prompt,
                                                      max_tokens=settings.RAG.MAX_TOKEN,
                                                      messages=json.dumps([msg.model_dump() for msg in messages], ensure_ascii=False),
                                                      )

        except AioRpcError as e:
            logger.error(str(e))
            raise ChatException(e)
        except Exception as e:  # noqa BLE001
            logger.error(str(e))
            raise ChatException(e)

        if response.status_code == 200:
            messages.insert(0, SystemMessage(role="system", content=system_prompt))
            messages.append(AssistantMessage(role="assistant", content=response.reply))
            return messages

        msg = f"Intent classification failed with status code {response.status_code} and reply: {response.response}"
        logger.error(msg)
        raise ChatException(msg)

    async def _enrich_data_for_rag(self, text_query: str, limit=10) -> str:

        try:
            response = await self._text_vector.get_similar_fragments(text=text_query, limit=limit)
        except AioRpcError as e:
            logger.error(str(e))
            raise ChatException(e)
        except Exception as e:  # noqa BLE001
            logger.error(str(e))
            raise ChatException(e)

        result = []
        if isinstance(response, list):
            for item in response:
                result.append(item.get("text", ""))

        return "\n".join(result)

    async def handle_unknown_intent(self, messages: list, answer: str) -> list:
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

        messages.append(AssistantMessage(role="assistant",
                                         content="Ничего не понял, но очень интересно"))

        return messages


@lru_cache
def get_chat_service(
        llm_client=Depends(get_llm_client),
        text_vector_client=Depends(get_text_vector_client)

) -> ChatService:
    return ChatService(
        llm_client,
        text_vector_client
    )
