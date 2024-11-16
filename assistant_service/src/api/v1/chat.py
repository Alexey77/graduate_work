from http import HTTPStatus

from core.logger import get_logger
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemes import ChatMessage, ReplyResponseModel, UserMessage
from services.auth import AuthService, get_auth_service
from services.chats import ChatService, get_chat_service
from services.exception import ServiceException

router = APIRouter()
security = HTTPBearer()
logger = get_logger(__name__)


@router.post("/chat",
             status_code=HTTPStatus.OK,
             response_model=ReplyResponseModel)
async def chat(
        request: Request,
        question_message: UserMessage | list[ChatMessage],
        credentials: HTTPAuthorizationCredentials = Depends(security),
        chat_service: ChatService = Depends(get_chat_service),
        auth_service: AuthService = Depends(get_auth_service),
):
    access_token = credentials.credentials # noqa F841
    user = await auth_service.get_current_user(
        access_token,
        request_id=request.headers.get('X-Request-Id'),
        external_validation=True
    )

    try:
        messages = await chat_service.get_answer(messages=[question_message], user=user.email)
    except ServiceException:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
        )

    return ReplyResponseModel(messages=messages)
