from http import HTTPStatus
from typing import Annotated

from core.logger import get_logger
from fastapi import APIRouter, Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemes import (
    ReplyResponseModel,
    RequestAsk,
    RequestReply,
    ResponseCreatedAsk,
    ResponseCreatedUnauthorizedAsk,
)
from services.assistants import AssistantsService, get_assistants_service
from services.auth import AuthService, get_auth_service

router = APIRouter()

security = HTTPBearer()

logger = get_logger(__name__)


@router.post("/ask",
             status_code=HTTPStatus.CREATED,
             response_model=ResponseCreatedAsk)
async def ask(
        request_ask: RequestAsk,
        credentials: HTTPAuthorizationCredentials = Depends(security),

        assist_service: AssistantsService = Depends(get_assistants_service),
        auth_service: AuthService = Depends(get_auth_service),

        user_agent: Annotated[str | None, Header()] = None
):
    access_token = credentials.credentials

    if access_token is None or not await auth_service.validate_access_token(access_token):
        logger.info("Authorization without a access token or the token is not valid")
        return ResponseCreatedUnauthorizedAsk()

    user = await auth_service.get_login_from_access_token(access_token=access_token)

    if user is None:
        logger.info("Authorization of an unknown user")
        return ResponseCreatedUnauthorizedAsk()

    id_ask = await assist_service.create_or_update_dialogue(content=request_ask.content,
                                                            id_dialog=request_ask.dialogue,
                                                            # dialogue=request_ask.dialogue,
                                                            user=user)

    return ResponseCreatedAsk(id_ask=id_ask)


@router.post("/reply",
             status_code=HTTPStatus.OK,
             response_model=ReplyResponseModel)
async def reply(
        request_reply: RequestReply,

        assist_service: AssistantsService = Depends(get_assistants_service),
        auth_service: AuthService = Depends(get_auth_service),

        authorization: str | None = Header(None),
        user_agent: Annotated[str | None, Header()] = None
):
    if authorization is None:  # TODO and other conditions
        messages = await assist_service.unauthorized_reply()
        return ReplyResponseModel(messages=messages)

