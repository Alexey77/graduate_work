from uuid import UUID

from pymongo.results import InsertOneResult

from . import AsyncMongoBase, AsyncMongoClient


class DialoguesMongoDB(AsyncMongoBase):
    def __init__(self, client: AsyncMongoClient, db_name: str, collection_name: str):
        super().__init__(client)
        self._db_name = db_name
        self._collection_name = collection_name

    async def find_dialog_by_id(self, _id: UUID | str) -> dict | None:
        if isinstance(_id, UUID):
            _id = str(_id)
        query = {"_id": _id}
        return await self._find_one(self._db_name, self._collection_name, query)

    async def add_new_dialogue(self, dialog: dict) -> InsertOneResult:
        return await self._insert_one(self._db_name, self._collection_name, dialog)
