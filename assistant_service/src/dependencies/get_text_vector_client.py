from fastapi import Depends, FastAPI

from text_vector_service import TextVectorClient

from .get_app import get_app


def get_text_vector_client(app: FastAPI = Depends(get_app)) -> TextVectorClient:
    return app.state.text_vector
