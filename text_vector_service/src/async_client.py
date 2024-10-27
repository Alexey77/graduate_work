# Тестовый клиент
import asyncio
import sys
import warnings
from pathlib import Path

import grpc

warnings.filterwarnings("ignore", category=UserWarning)
# ruff: noqa: E402
current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir / 'grpc_generated'))

from grpc_generated import encoder_pb2, encoder_pb2_grpc


# ruff: noqa: T201
async def run():
    phrase = "Привет, мир!"

    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = encoder_pb2_grpc.EncoderServiceStub(channel)

        encode_request = encoder_pb2.EncodeRequest(
            text=phrase,
            # model_name="intfloat/multilingual-e5-large"
        )

        response = await stub.Encode(encode_request)

        print(f"Encoded vector: {response.vector[0:10]}")
        print(f"Model used: {response.model_name}")

        encode_request = encoder_pb2.EncodeRequest(
            text=phrase,
            # model_name="intfloat/multilingual-e5-large"
        )

        response = await stub.CountTokens(encode_request)

        print(f"CountTokens token_count: {response.token_count}")
        print(f"Model used: {response.model_name}")


if __name__ == "__main__":
    asyncio.run(run())
