import json

from core.config import IntentSettings
from core.logger import get_logger
from llm import LLMClient, LLMException
from schemes import LLMResponse

from .exception import IntentException

logger = get_logger(__name__)




async def determine_intent(messages: list[dict[str, str]],
                           llm_client: LLMClient,
                           settings: IntentSettings,
                           **kwargs) -> dict[str, str]:
    try:
        response = await llm_client.get_functions(service=settings.SERVICE,
                                                                      model=settings.MODEL,
                                                                      system=system_prompt["eng"],
                                                                      max_tokens=kwargs.get("max_tokens", 150),
                                                                      messages=json.dumps(messages, ensure_ascii=False),
                                                                      functions=json.dumps(functions_desc, ensure_ascii=False),
                                                                      function_call=kwargs.get("function_call", "auto")
                                                                      )




    except LLMException as e:
        logger.error(str(e))
        raise IntentException

    if response.status_code == 200:
        return json.loads(response.reply)

    logger.error(f"Intent classification failed with status code {response.status_code} and reply: {response.response}")
    raise IntentException


