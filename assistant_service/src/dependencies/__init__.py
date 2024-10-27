from core.config import settings
from database.mongodb import AsyncMongoClient
from database.mongodb.dialog import DialoguesMongoDB
from fastapi import Depends, FastAPI


def get_app() -> FastAPI:
    from main import app
    return app


def get_mongo(app: FastAPI = Depends(get_app)) -> AsyncMongoClient:
    return app.state.mongo


def get_db_dialogue(mongo: AsyncMongoClient = Depends(get_mongo)) -> DialoguesMongoDB:
    return DialoguesMongoDB(client=mongo,
                            db_name=settings.MONGO.DB_NAME,
                            collection_name=settings.MONGO.COLLECTION_NAME)

# def get_db(app: FastAPI = Depends(get_app)) -> DatabaseConnection:
#     return app.state.db
