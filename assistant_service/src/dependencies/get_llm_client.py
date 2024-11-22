from fastapi import Depends, FastAPI
from llm import LLMClient

from .get_app import get_app


def get_llm_client(app: FastAPI = Depends(get_app)) -> LLMClient:
    return app.state.llm
