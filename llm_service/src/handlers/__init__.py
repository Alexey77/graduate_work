import json
import sys
from pathlib import Path

import grpc
from core.logger import get_logger
from grpc import StatusCode

current_dir = Path(__file__).parent.parent.resolve()
grpc_generated_path = current_dir / 'grpc_generated'
sys.path.insert(0, str(grpc_generated_path))

from grpc_generated.llm_pb2 import (
    LLMRequest,
    LLMResponse,
)
from networking.exception import NetworkException
from services.factory import get_llm_service

current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir / 'grpc_generated'))

# ruff: noqa: E402
from grpc_generated import llm_pb2, llm_pb2_grpc

logger = get_logger(__name__)


class LLMHandler(llm_pb2_grpc.LlmServiceServicer):
    async def GetCompletion(
            self,
            request,
            context: grpc.aio.ServicerContext
    ) -> LLMResponse:

        try:
            service_name: str = llm_pb2.ApiServiceName.Name(request.service)
            logger.info(f"Received request with service: {service_name} and model: {request.model}")
            service = get_llm_service(service_name)

            messages: list[dict] = json.loads(request.messages)
            logger.debug("Parsed dialogue successfully")

            data = service.prepare_data(
                model_name=request.model,
                system_prompt=request.system,
                max_tokens=request.max_tokens,
                messages=messages
            )
            logger.debug(f"Data prepared for service request: {data}")

            headers = service.prepare_headers()

            status_code, response = await service.send_post(
                data=data,
                headers=headers
            )
            logger.info(f"Request processed successfully with status code: {status_code}")

            reply = json.dumps(service.get_reply(response=response), ensure_ascii=False)
            response = json.dumps(response, ensure_ascii=False)

            return LLMResponse(
                status_code=status_code,
                reply=reply,
                response=response
            )

        except NetworkException as e:
            logger.error(f"NetworkException encountered:{e}")
            context.set_code(StatusCode.UNAVAILABLE)
            context.set_details(str(e))
            return LLMResponse(
                status_code=503,
                response=str(e)
            )
        except Exception as e: # noqa: BLE001
            msg = f"Unhandled exception encountered:{e}"
            logger.error(msg)
            context.set_code(StatusCode.INTERNAL)
            context.set_details(str(e))
            return LLMResponse(
                status_code=500,
                response=str(e)
            )
