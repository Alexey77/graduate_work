from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, NetworkTimeout, OperationFailure
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from core.logger import get_logger

from .exception import MongoDBException

logger = get_logger(__name__)


class AsyncMongoClient:
    def __init__(self, uri: str):
        self._uri = uri
        self._client = AsyncIOMotorClient(self._uri)
        logger.info("Initialized MongoDB client.")

    @property
    def client(self):
        return self._client

    async def close(self):
        logger.info("Closing MongoDB client.")
        self._client.close()

    def __del__(self):
        if hasattr(self, "_client"):
            logger.info("MongoDB client is being garbage collected and closed.")
            self._client.close()


class AsyncMongoBase:
    def __init__(self, client: AsyncMongoClient) -> None:
        self._client = client.client

    async def _insert_one(self, database: str, collection: str, document: dict) -> InsertOneResult:
        try:
            result = await self._client[database][collection].insert_one(document)
            logger.info("Document inserted successfully")
            return result
        except (OperationFailure, NetworkTimeout, ConnectionFailure) as e:
            error_message = f"Insert operation failed: {str(e)}"
            logger.error(error_message)
            raise MongoDBException(error_message)

    async def _find_one(self, database: str, collection: str, filter: dict) -> dict | None:
        try:
            result = await self._client[database][collection].find_one(filter)
            logger.info("Document found successfully")
            return result
        except (OperationFailure, NetworkTimeout, ConnectionFailure) as e:
            error_message = f"Find operation failed: {str(e)}"
            logger.error(error_message)
            raise MongoDBException(error_message)

    async def _find_many(self, database: str, collection: str, filter: dict) -> list[dict]:
        try:
            cursor = self._client[database][collection].find(filter)
            result = await cursor.to_list(length=None)
            logger.info("Documents found successfully")
            return result
        except (OperationFailure, NetworkTimeout, ConnectionFailure) as e:
            error_message = f"Find operation failed: {str(e)}"
            logger.error(error_message)
            raise MongoDBException(error_message)

    async def _update_one(self, database: str, collection: str, filter: dict, update: dict) -> UpdateResult:
        try:
            result = await self._client[database][collection].update_one(filter, update)
            logger.info("Document updated successfully")
            return result
        except (OperationFailure, NetworkTimeout, ConnectionFailure) as e:
            error_message = f"Update operation failed: {str(e)}"
            logger.error(error_message)
            raise MongoDBException(error_message)

    async def _delete_one(self, database: str, collection: str, filter: dict) -> DeleteResult:
        try:
            result = await self._client[database][collection].delete_one(filter)
            logger.info("Document deleted successfully")
            return result
        except (OperationFailure, NetworkTimeout, ConnectionFailure) as e:
            error_message = f"Delete operation failed: {str(e)}"
            logger.error(error_message)
            raise MongoDBException(error_message)

    async def _aggregate(self, database: str, collection: str, pipeline: list[dict]) -> list[dict]:
        try:
            cursor = self._client[database][collection].aggregate(pipeline)
            result = await cursor.to_list(length=None)
            logger.info("Aggregation completed successfully")
            return result
        except (OperationFailure, NetworkTimeout, ConnectionFailure) as e:
            error_message = f"Aggregation failed: {str(e)}"
            logger.error(error_message)
            raise MongoDBException(error_message)
