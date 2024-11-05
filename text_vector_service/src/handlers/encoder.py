from core.logger import get_logger
from grpc_generated import encoder_pb2, encoder_pb2_grpc
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = get_logger(__name__)


class EncoderServicer(encoder_pb2_grpc.EncoderServiceServicer):
    def __init__(self, manager_model):
        self.manager_model = manager_model
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    def Encode(self, request, context):
        model = self.manager_model.get_model("intfloat/multilingual-e5-small")
        vector = model.encode(request.text).tolist()
        return encoder_pb2.EncodeResponse(vector=vector)

    def CountTokens(self, request, context):
        model = self.manager_model.get_model("intfloat/multilingual-e5-small")
        token_count = len(model.tokenizer.encode(request.text, add_special_tokens=False))


        return encoder_pb2.CountTokensResponse(token_count=token_count)

    def SplitText(self, request, context):
        self.text_splitter.chunk_size = request.chunk_size
        self.text_splitter.chunk_overlap = request.overlap
        fragments = self.text_splitter.split_text(request.text)

        return encoder_pb2.SplitTextResponse(fragments=fragments)
