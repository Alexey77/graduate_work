import json
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import UUID4, BaseModel, Field, model_validator


# Request
class RequestAsk(BaseModel):
    dialogue: UUID4 | None = None
    content: Annotated[str, Field(min_length=1, max_length=4096)]


class RequestReply(BaseModel):
    id_ask: UUID4


class SystemMessage(BaseModel):
    role: Literal["system"]
    content: Annotated[str, Field(min_length=1, max_length=4_096)]


class UserMessage(BaseModel):
    role: Literal["user"]
    content: Annotated[str, Field(min_length=1, max_length=4_096)]


class AssistantMessage(BaseModel):
    role: Literal["assistant"]
    content: Annotated[str, Field(min_length=1, max_length=16_384)]


# Response

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: Annotated[str, Field(min_length=1, max_length=4096)]


class ChatResponse(BaseModel):
    messages: list[ChatMessage]


class ResponseCreatedAsk(BaseModel):
    id_ask: UUID4


class LLMResponse(BaseModel):
    status_code: int
    reply: str
    response: str | dict

    @model_validator(mode="before")
    def parse_response(cls, values):
        if "response" in values and isinstance(values["response"], str):
            values["response"] = json.loads(values["response"].strip(' "\''))
        if "reply" in values and isinstance(values["reply"], str):
            values["reply"] = values["reply"].strip(' "\'')
        return values


class ResponseCreatedUnauthorizedAsk(ResponseCreatedAsk):
    id_ask: UUID4 = UUID("77777777-7777-4777-8777-777777777777")


class Role(str, Enum):
    user = "user"
    guest = "guest"
    assistant = "assistant"


class ReplyResponseModel(BaseModel):
    messages: list[SystemMessage | UserMessage | AssistantMessage]


class ResponseMessage(BaseModel):
    message: str


class User(BaseModel):
    email: str
    roles: list[Role]
