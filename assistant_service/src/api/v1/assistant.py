from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Header
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


@router.post("/ask",
             status_code=HTTPStatus.CREATED,
             response_model=ResponseCreatedAsk)
async def ask(
        request_ask: RequestAsk,

        assist_service: AssistantsService = Depends(get_assistants_service),
        auth_service: AuthService = Depends(get_auth_service),

        authorization: str | None = Header(None),
        user_agent: Annotated[str | None, Header()] = None
):
    if authorization is None \
            or not auth_service.validate_access_token(authorization) \
            or auth_service.get_login_from_access_token(access_token=authorization) is None:
        return ResponseCreatedUnauthorizedAsk()

    return ResponseCreatedUnauthorizedAsk()


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

    # return ResponseMessage(message="Service is running")
