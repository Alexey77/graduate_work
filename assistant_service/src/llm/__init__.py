import sys
import warnings
from pathlib import Path

from core.logger import get_logger
from llm.exception import LLMException
from schemes import LLMResponse
from icecream import ic # TODO убрать

warnings.filterwarnings("ignore", category=UserWarning)

import grpc

logger = get_logger(__name__)

current_dir = Path(__file__).parent.parent.resolve()
# ruff: noqa: E402
grpc_generated_path = current_dir / 'grpc_generated'
sys.path.insert(0, str(grpc_generated_path))

from grpc_generated import (llm_pb2, llm_pb2_grpc, similarity_search_pb2,
                            similarity_search_pb2_grpc)


class LLMClient:
    def __init__(self, address: str):
        self.address = address
        self.channel: grpc.aio.Channel | None = None
        self.stub: llm_pb2_grpc.LlmServiceStub | None = None

    async def get_completion(
            self,
            service: llm_pb2.ApiServiceName,
            model: str,
            system: str,
            max_tokens: int,
            messages: str
    ) -> LLMResponse:
        async with grpc.aio.insecure_channel(self.address) as channel:
            stub = llm_pb2_grpc.LlmServiceStub(channel)

            request = llm_pb2.LLMRequest(
                service=service,
                model=model,
                system=system,
                max_tokens=max_tokens,
                messages=messages
            )

            try:
                response: llm_pb2.LLMResponse = await stub.GetCompletion(request)

                return LLMResponse(
                    status_code=response.status_code,
                    reply=response.reply,
                    response=response.response
                )
            except grpc.aio.AioRpcError as e:
                msg = f"gRPC error: {e.code()} - {e.details()}"
                logger.error(msg)
                raise LLMException(msg)

    async def get_functions(
            self,
            service: llm_pb2.ApiServiceName,
            model: str,
            system: str,
            max_tokens: int,
            messages: str,
            functions: str,
            function_call: str
    ) -> LLMResponse:

        ic(self.address)


        async with grpc.aio.insecure_channel(self.address) as channel:
            stub = llm_pb2_grpc.LlmServiceStub(channel)

            ic(stub)

            request = llm_pb2.LLMFunctionRequest(
                service=service,
                model=model,
                system=system,
                max_tokens=max_tokens,
                messages=messages,
                functions=functions,
                function_call=function_call
            )

            ic(request)

            try:
                response: llm_pb2.LLMFunctionResponse = await stub.GetFunctions(request)

                return LLMResponse(
                    status_code=response.status_code,
                    reply=response.reply,
                    response=response.response
                )
            except grpc.aio.AioRpcError as e:
                msg = f"gRPC error: {e.code()} - {e.details()}"
                logger.error(msg)
                raise LLMException(msg)
