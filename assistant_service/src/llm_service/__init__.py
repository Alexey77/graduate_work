import sys
import warnings
from pathlib import Path

from core.logger import get_logger
from schemes import RAGResponse

warnings.filterwarnings("ignore", category=UserWarning)

import grpc

logger = get_logger(__name__)

current_dir = Path(__file__).parent.parent.resolve()
# ruff: noqa: E402
grpc_generated_path = current_dir / 'grpc_generated'
sys.path.insert(0, str(grpc_generated_path))

from grpc_generated import llm_pb2, llm_pb2_grpc


class LLMClient:
    def __init__(self, address: str):
        """
        Initialize the LLMClient.

        Args:
            address (str): Address of the gRPC service, e.g., "localhost:50051".
        """
        self.address = address
        self.channel: grpc.aio.Channel | None = None
        self.stub: llm_pb2_grpc.LlmServiceStub | None = None

    async def connect(self) -> None:
        """
        Establish an asynchronous connection to the gRPC service and initialize the stub.
        """
        if self.channel is None:
            self.channel = grpc.aio.insecure_channel(self.address)
            await self.channel.channel_ready()
            self.stub = llm_pb2_grpc.LlmServiceStub(self.channel)
            logger.info("Connected to gRPC LLM service at", self.address)

    async def get_completion(
            self,
            service: llm_pb2.ApiServiceName,
            model: str,
            system: str,
            max_tokens: int,
            messages: str
    ) -> RAGResponse:
        """
        Send a GetCompletion request to the gRPC service.

        Args:
            service (llm_pb2.ApiServiceName): Name of the API service.
            model (str): Model name.
            system (str): System prompt.
            max_tokens (int): Maximum number of tokens.
            messages (str): Dialogue text.

        Returns:
            llm_pb2.LLMResponse: Response from the service.
        """
        if self.stub is None:
            await self.connect()

        request: llm_pb2.LLMRequest = llm_pb2.LLMRequest(
            service=service,
            model=model,
            system=system,
            max_tokens=max_tokens,
            messages=messages
        )

        try:
            response: llm_pb2.LLMResponse = await self.stub.GetCompletion(request)

            return RAGResponse(status_code=response.status_code,
                               reply=response.reply,
                               response=response.response)
        except grpc.aio.AioRpcError as e:
            msg = f"gRPC error: {e.code()} - {e.details()}"
            logger.error(msg)
            raise

    async def disconnect(self) -> None:
        """
        Close the asynchronous connection to the gRPC service.
        """
        if self.channel:
            await self.channel.close()
            self.channel = None
            self.stub = None
            logger.info("Disconnected from gRPC LLM service.")
