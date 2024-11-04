import grpc
from grpc_generated import similarity_search_pb2, similarity_search_pb2_grpc
from qdrant_client import QdrantClient, models
from core.logger import get_logger
import json
logger = get_logger(__name__)


class SimilaritySearchServicer(similarity_search_pb2_grpc.SimilaritySearchServiceServicer):
    def __init__(self, settings, manager_model):
        self.settings = settings
        self.manager_model = manager_model
        self.qdrant_client = QdrantClient(host=settings.HOST, port=settings.PORT)

    async def SearchSimilarFragments(self, request, context):
        try:
            model_name = request.model_name
            model = self.manager_model.get_model(model_name)
            if model is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Model '{model_name}' not found.")
                return similarity_search_pb2.SearchResponse()

            query_vector = model.encode(request.text).tolist()

            try:
                search_results = self.qdrant_client.search(
                    collection_name=request.collection,
                    query_vector=query_vector,
                    limit=request.limit
                )
            except Exception as e:
                logger.error(f"Error searching Qdrant: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return similarity_search_pb2.SearchResponse()

            fragment_results = []
            for result in search_results:
                fragment_results.append(
                    similarity_search_pb2.FragmentResult(
                        text=result.payload.get("source", ""),
                        meta=json.dumps(result.payload.get("metadata", {})),
                        score=result.score
                    )
                )

            return similarity_search_pb2.SearchResponse(similar_fragments=fragment_results)

        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return similarity_search_pb2.SearchResponse()