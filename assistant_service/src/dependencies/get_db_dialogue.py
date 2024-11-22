from core.config import settings
from database.mongodb import AsyncMongoClient
from database.mongodb.dialog import DialoguesMongoDB
from fastapi import Depends

from .get_mongo import get_mongo


def get_db_dialogue(mongo: AsyncMongoClient = Depends(get_mongo)) -> DialoguesMongoDB:
    return DialoguesMongoDB(client=mongo,
                            db_name=settings.MONGO.DB_NAME,
                            collection_name=settings.MONGO.COLLECTION_NAME)
