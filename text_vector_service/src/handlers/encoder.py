from core.logger import get_logger
from grpc_generated import encoder_pb2, encoder_pb2_grpc
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = get_logger(__name__)


class EncoderServicer(encoder_pb2_grpc.EncoderServiceServicer):
    def __init__(self, manager_model):
        self.manager_model = manager_model
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    def Encode(self, request, context):
        model_name = request.model_name
        model = self.manager_model.get_model(model_name)
        vector = model.encode(request.text).tolist()
        try:
            first_module = model._first_module()
            if hasattr(first_module, 'auto_model'):  # Check if it's a Hugging Face model
                if hasattr(first_module.auto_model.config, '_name_or_path'):
                    model_name_to_return = first_module.auto_model.config._name_or_path
                # Add any other known internal structure checks here if needed in the future
                else:
                    model_name_to_return = "Unknown Model Name (No _name_or_path)"  # Better default
            else:
                model_name_to_return = "Unknown Model Type (No auto_model)"

        except AttributeError:
            model_name_to_return = "Unknown Model Name (AttributeError)"


        return encoder_pb2.EncodeResponse(vector=vector, model_name=model_name_to_return)

    def CountTokens(self, request, context):
        model_name = request.model_name
        model = self.manager_model.get_model(model_name)
        token_count = len(model.tokenizer.encode(request.text, add_special_tokens=False))

        model_name_to_return = getattr(model, 'model_name_or_path', 'Unknown Model Name')

        return encoder_pb2.CountTokensResponse(token_count=token_count, model_name=model_name_to_return)

    def SplitText(self, request, context):
        self.text_splitter.chunk_size = request.chunk_size
        self.text_splitter.chunk_overlap = request.overlap
        fragments = self.text_splitter.split_text(request.text)

        return encoder_pb2.SplitTextResponse(fragments=fragments)
