from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.logger import get_logger
from grpc_generated.encoder_pb2_grpc import EncoderServiceServicer
from model_manager import ModelManager

from grpc_generated.encoder_pb2 import (
    CountTokensResponse,
    EncodeResponse,
    SplitTextResponse,
)

logger = get_logger(__name__)


class EncoderServicer(EncoderServiceServicer):

    def __init__(self, manager_model: ModelManager):
        self._model_manager = manager_model

    def Encode(self, request, context):
        logger.info(f"Received Encode request: text='{request.text[:32]}...', model_name='{request.model_name}'")

        model = self._model_manager.get_model(model_name=request.model_name)

        return EncodeResponse(
            vector=model.encode(sentences=request.text),
            model_name=request.model_name
        )

    def CountTokens(self, request, context):
        logger.info(f"Received CountTokens request:text='{request.text[:32]}...', model_name='{request.model_name}'")

        model = self._model_manager.get_model(model_name=request.model_name)
        encoding = model.tokenizer(request.text, return_tensors='pt', truncation=False)

        return CountTokensResponse(
            token_count=len(encoding['input_ids'][0]),
            model_name=request.model_name
        )

    def SplitText(self, request, context):
        logger.info(f"Received SplitText request: text='{request.text[:32]}...', chunk_size={request.chunk_size}, overlap={request.overlap}")

        chunk_size = request.chunk_size if request.chunk_size != 0 else 255
        overlap = request.overlap if request.overlap != 0 else 50

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            is_separator_regex=False,
        )

        fragments = text_splitter.split_text(request.text)
        return SplitTextResponse(fragments=fragments)
