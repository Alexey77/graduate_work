from database.mongodb import AsyncMongoClient
from fastapi import Depends, FastAPI

from .get_app import get_app


def get_mongo(app: FastAPI = Depends(get_app)) -> AsyncMongoClient:
    return app.state.mongo
