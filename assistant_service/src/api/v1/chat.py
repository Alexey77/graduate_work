from http import HTTPStatus

from core.logger import get_logger
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemes import ChatMessage, ReplyResponseModel, UserMessage
from services.chats import ChatService, get_chat_service
from services.exception import ServiceException

router = APIRouter()
security = HTTPBearer()
logger = get_logger(__name__)


@router.post("/chat",
             status_code=HTTPStatus.OK,
             response_model=ReplyResponseModel)
async def chat(
        question_message: UserMessage | list[ChatMessage],
        credentials: HTTPAuthorizationCredentials = Depends(security),
        chat_service: ChatService = Depends(get_chat_service),
        # auth_service: AuthService = Depends(get_auth_service),
        # user_agent: Annotated[str | None, Header()] = None
):
    access_token = credentials.credentials # noqa F841

    # Authorization code can be uncommented if needed
    # if access_token is None or not await auth_service.validate_access_token(access_token):
    #     logger.info("Authorization without a access token or the token is not valid")
    #     raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
    #                         detail="Authorization without a access token or the token is not valid",
    #                         headers={"WWW-Authenticate": "Bearer"})
    #
    # user = await auth_service.get_login_from_access_token(access_token=access_token)
    #
    # if user is None:
    #     logger.info("Authorization of an unknown user")
    #     raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
    #                         detail="Authorization without a access token or the token is not valid",
    #                         headers={"WWW-Authenticate": "Bearer"})

    try:
        messages = await chat_service.get_answer(messages=[question_message], user="ddd")
    except ServiceException:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
        )

    return ReplyResponseModel(messages=messages)
