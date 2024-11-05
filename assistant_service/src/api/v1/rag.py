from http import HTTPStatus
from typing import Annotated

from core.logger import get_logger
from fastapi import APIRouter, Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemes import (
    QuestionMessage,
    ReplyResponseModel,
    Role,
)
from services.auth import AuthService, get_auth_service
from services.rag_service import RAGService, get_rag_service

router = APIRouter()

security = HTTPBearer()

logger = get_logger(__name__)


@router.post("/rag",
             status_code=HTTPStatus.OK,
             response_model=ReplyResponseModel)
async def question(
        question_message: QuestionMessage,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        questions_service: RAGService = Depends(get_rag_service),
        auth_service: AuthService = Depends(get_auth_service),
        user_agent: Annotated[str | None, Header()] = None
):
    access_token = credentials.credentials  # noqa F841
    user = await auth_service.get_current_user(access_token, external_validation=True)
    logger.info("User %s asked a question: %s", user.email, question_message.content)

    response = await questions_service.get_answer(messages={"role": Role.user.value,
                                                            "content": question_message.content})

    return response
