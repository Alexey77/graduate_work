from uuid import UUID

from . import AsyncMongoBase, AsyncMongoClient


class DialoguesMongoDB(AsyncMongoBase):
    def __init__(self, mongo_client: AsyncMongoClient, db_name: str, collection_name: str):
        super().__init__(mongo_client)
        self._db_name = db_name
        self._collection_name = collection_name

    async def find_dialog_by_id(self, _id: UUID) -> dict | None:
        query = {"_id": _id}
        return await self._find_one(self._db_name, self._collection_name, query)
