import json

import grpc
from core.logger import get_logger
from grpc_generated import similarity_search_pb2, similarity_search_pb2_grpc
from qdrant_client import QdrantClient

logger = get_logger(__name__)


class SimilaritySearchServicer(similarity_search_pb2_grpc.SimilaritySearchServiceServicer):
    def __init__(self, settings, manager_model):
        self.settings = settings
        self.manager_model = manager_model
        self.qdrant_client = QdrantClient(host=settings.HOST, port=settings.PORT)

    async def SearchSimilarFragments(self, request, context):
        logger.info(f"Received search request: text='{request.text}', collection='{request.collection}', limit={request.limit}")

        try:
            model = self.manager_model.get_model("intfloat/multilingual-e5-small")
            if model is None:
                logger.warning("Model intfloat/multilingual-e5-small not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Model intfloat/multilingual-e5-small not found.")
                return similarity_search_pb2.SearchResponse()

            logger.info("Encoding query text into vector")
            query_vector = model.encode(request.text).tolist()

            try:
                logger.info(f"Searching in collection '{request.collection}' with limit {min(request.limit, 10)}")
                search_results = self.qdrant_client.search(
                    collection_name=request.collection,
                    query_vector=query_vector,
                    limit=min(request.limit, 10)
                )
            except (ValueError, TypeError) as e:
                logger.error(f"Error searching Qdrant: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Error processing the search request.")
                return similarity_search_pb2.SearchResponse()

            fragment_results = []
            for result in search_results:
                meta = {
                    "page_id": result.payload.get("page_id"),
                    "title": result.payload.get("title"),
                    "time_request": result.payload.get("time_request"),
                }

                fragment_results.append(
                    similarity_search_pb2.FragmentResult(
                        text=result.payload.get("text", ""),
                        meta=json.dumps(meta, ensure_ascii=False),
                        score=result.score
                    )
                )

            logger.info("Returning search response with results")
            return similarity_search_pb2.SearchResponse(similar_fragments=fragment_results)

        except (grpc.RpcError, ValueError, TypeError) as e:
            logger.error(f"Error during similarity search: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Internal server error occurred.")
            return similarity_search_pb2.SearchResponse()
