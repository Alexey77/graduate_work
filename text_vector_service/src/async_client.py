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

from grpc_generated import (
    encoder_pb2,
    encoder_pb2_grpc,
    similarity_search_pb2,
    similarity_search_pb2_grpc,
)


# ruff: noqa: T201
async def run():
    phrase = "С конца 1811-го года началось усиленное вооружение и сосредоточение сил Западной Европы, и в 1812 году силы эти -- миллионы людей"

    async with grpc.aio.insecure_channel('0.0.0.0:50052') as channel:
        stub = encoder_pb2_grpc.EncoderServiceStub(channel)

        encode_request = encoder_pb2.EncodeRequest(
            text=phrase
        )

        response = await stub.Encode(encode_request)

        print(f"Encoded vector: {response.vector[0:10]}")

        encode_request = encoder_pb2.EncodeRequest(
            text=phrase
        )

        response = await stub.CountTokens(encode_request)

        print(f"CountTokens token_count: {response.token_count}")

        similarity_stub = similarity_search_pb2_grpc.SimilaritySearchServiceStub(channel)
        similarity_request = similarity_search_pb2.SearchRequest(
            text=phrase,
            collection="text_fragments",
            limit=5
        )

        similarity_response = await similarity_stub.SearchSimilarFragments(similarity_request)

        print("Similarity search results:")
        for result in similarity_response.similar_fragments:
            print(f"Text: {result.text}, Score: {result.score}, Meta: {result.meta}")


if __name__ == "__main__":
    asyncio.run(run())
